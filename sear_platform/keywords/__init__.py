# Import the KeywordExtractor class from the local extractor module.
# This component is responsible for identifying and extracting relevant 
# keywords and key phrases from raw text or HTML content for SEO analysis.
from .extractor import KeywordExtractor

# Import the PersianTextProcessor class from the local processor module.
# This utility handles language-specific text normalization, cleaning, 
# and preprocessing tasks (such as handling zero-width non-joiners and 
# standardizing characters) which are essential for accurate Persian NLP 
# and SEO keyword analysis.
from .processor import PersianTextProcessor