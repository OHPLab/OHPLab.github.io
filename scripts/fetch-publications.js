const fs = require('fs/promises');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const PUBLICATIONS_FILE = path.join(ROOT, 'data', 'publications.json');
const PENDING_FILE = path.join(ROOT, 'data', 'publications.pending.json');

const OPENALEX_API = 'https://api.openalex.org';
const MENTOR = {
  englishName: 'Jialin Fan',
  orcid: '0000-0003-1530-4739',
  institutionKeywords: ['Shenzhen University', '深圳大学']
};

const mailto = process.env.OPENALEX_MAILTO;

function normalizeTitle(title = '') {
  return title
    .toLowerCase()
    .replace(/<[^>]*>/g, '')
    .replace(/[^\p{L}\p{N}]+/gu, ' ')
    .trim();
}

function normalizeDoi(doi = '') {
  return String(doi)
    .toLowerCase()
    .replace(/^https?:\/\/(dx\.)?doi\.org\//, '')
    .trim();
}

async function readJson(file, fallback) {
  try {
    return JSON.parse(await fs.readFile(file, 'utf8'));
  } catch (error) {
    if (error.code === 'ENOENT') return fallback;
    throw error;
  }
}

async function openAlexGet(endpoint, params = {}) {
  const url = new URL(endpoint, OPENALEX_API);
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      url.searchParams.set(key, value);
    }
  }
  if (mailto && !url.searchParams.has('mailto')) {
    url.searchParams.set('mailto', mailto);
  }

  const response = await fetch(url, {
    headers: { Accept: 'application/json' }
  });

  if (!response.ok) {
    throw new Error(`OpenAlex request failed: ${response.status} ${response.statusText} (${url})`);
  }

  return response.json();
}

async function findOpenAlexAuthorId() {
  const orcidUrl = `https://orcid.org/${MENTOR.orcid}`;
  const filters = [
    `orcid:${MENTOR.orcid}`,
    `orcid:${orcidUrl}`
  ];

  for (const filter of filters) {
    try {
      const data = await openAlexGet('/authors', {
        filter,
        per_page: '5'
      });
      const author = (data.results || []).find(item => {
        const itemOrcid = String(item.orcid || '').toLowerCase();
        return itemOrcid.includes(MENTOR.orcid);
      });
      if (author && author.id) return author.id;
    } catch (error) {
      console.warn(`OpenAlex author lookup skipped for ${filter}: ${error.message || error}`);
    }
  }

  return '';
}

function workHasMentor(work) {
  return (work.authorships || []).some(authorship => {
    const author = authorship.author || {};
    const displayName = String(author.display_name || '').toLowerCase();
    const orcid = String(author.orcid || '').toLowerCase();
    return orcid.includes(MENTOR.orcid) || displayName === MENTOR.englishName.toLowerCase();
  });
}

function workHasInstitutionKeyword(work) {
  const haystack = (work.authorships || [])
    .flatMap(authorship => authorship.institutions || [])
    .map(institution => `${institution.display_name || ''} ${institution.display_name_alternatives || ''}`)
    .join(' ')
    .toLowerCase();

  return MENTOR.institutionKeywords.some(keyword => haystack.includes(keyword.toLowerCase()));
}

async function fetchWorks() {
  let works = [];

  const authorId = await findOpenAlexAuthorId();
  if (authorId) {
    const data = await openAlexGet('/works', {
      filter: `authorships.author.id:${authorId}`,
      sort: 'publication_date:desc',
      per_page: '200'
    });
    works = data.results || [];
  }

  if (!works.length) {
    const data = await openAlexGet('/works', {
      search: MENTOR.englishName,
      sort: 'publication_date:desc',
      per_page: '200'
    });
    works = (data.results || []).filter(work => workHasMentor(work) && workHasInstitutionKeyword(work));
  }

  return works;
}

function mapWork(work) {
  const primaryLocation = work.primary_location || {};
  const source = primaryLocation.source || work.host_venue || {};
  const doi = normalizeDoi(work.doi || '');
  const url = doi ? `https://doi.org/${doi}` : (primaryLocation.landing_page_url || work.openalex || '');

  return {
    title: work.title || work.display_name || '',
    authors: (work.authorships || []).map(authorship => authorship.author && authorship.author.display_name).filter(Boolean),
    journal: source.display_name || '',
    year: work.publication_year || null,
    publication_date: work.publication_date || '',
    doi,
    url,
    source: 'OpenAlex',
    openalex_id: work.id || '',
    confirmed: false,
    manual: false,
    category: work.type_crossref || work.type || ''
  };
}

function makeSeenSet(items) {
  const dois = new Set();
  const titles = new Set();

  for (const item of items) {
    const doi = normalizeDoi(item.doi || '');
    const title = normalizeTitle(item.title || '');
    if (doi) dois.add(doi);
    if (title) titles.add(title);
  }

  return { dois, titles };
}

function isKnown(item, seen) {
  const doi = normalizeDoi(item.doi || '');
  const title = normalizeTitle(item.title || '');

  if (doi && seen.dois.has(doi)) return true;
  if (!doi && title && seen.titles.has(title)) return true;
  if (doi && title && seen.titles.has(title)) return true;
  return false;
}

async function main() {
  const confirmed = await readJson(PUBLICATIONS_FILE, []);
  const existingPending = await readJson(PENDING_FILE, []);
  const seen = makeSeenSet([...confirmed, ...existingPending]);

  const works = await fetchWorks();
  const candidates = works
    .filter(workHasMentor)
    .map(mapWork)
    .filter(item => item.title)
    .filter(item => !isKnown(item, seen));

  const nextPending = [...existingPending, ...candidates].sort((a, b) => {
    const yearDiff = (b.year || 0) - (a.year || 0);
    if (yearDiff) return yearDiff;
    return String(b.publication_date || '').localeCompare(String(a.publication_date || ''));
  });

  await fs.mkdir(path.dirname(PENDING_FILE), { recursive: true });
  await fs.writeFile(PENDING_FILE, `${JSON.stringify(nextPending, null, 2)}\n`, 'utf8');
  console.log(`Fetched ${works.length} OpenAlex works; added ${candidates.length} pending publication(s).`);
}

main().catch(async error => {
  console.error(error.message || error);
  try {
    const existingPending = await readJson(PENDING_FILE, []);
    await fs.mkdir(path.dirname(PENDING_FILE), { recursive: true });
    await fs.writeFile(PENDING_FILE, `${JSON.stringify(existingPending, null, 2)}\n`, 'utf8');
  } catch (pendingError) {
    console.error(`Could not preserve pending publications: ${pendingError.message || pendingError}`);
  }
  process.exitCode = 0;
});
