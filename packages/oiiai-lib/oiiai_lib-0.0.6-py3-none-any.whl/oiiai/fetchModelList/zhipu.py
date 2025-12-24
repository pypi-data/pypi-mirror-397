"""
Zhipu AI model list fetching with multi-strategy parsing

This module provides robust HTML parsing for Zhipu's model documentation page
using multiple strategies including BeautifulSoup for reliable extraction.
"""

from html.parser import HTMLParser
import re
from typing import List, Dict, Optional, Tuple

import requests

try:
    from bs4 import BeautifulSoup

    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

from .__base__ import FetchBase

# Zhipu model documentation page
ZHIPU_MODEL_DOC_URL = "https://docs.bigmodel.cn/cn/guide/start/model-overview"

# Known Zhipu model name patterns for pattern-based extraction (Strategy 3)
ZHIPU_MODEL_PATTERNS = [
    r"glm-\d+(?:\.\d+)?[a-z]*(?:-[a-z0-9]+)*",  # glm-4, glm-4.5, glm-4-plus, glm-4.6v-flash
    r"chatglm[_-]?\d*[a-z]*",  # chatglm, chatglm3, chatglm_turbo
    r"codegeex-\d+[a-z]*",  # codegeex-4
    r"cogview-\d+[a-z]*(?:-[a-z]+)*",  # cogview-3, cogview-3-plus, cogview-4
    r"cogvideo[a-z]*-\d*[a-z]*",  # cogvideox-2
    r"embedding-\d+",  # embedding-2, embedding-3
    r"charglm-\d+",  # charglm-3
]

# Known category IDs in Zhipu documentation (Chinese)
ZHIPU_CATEGORY_IDS = [
    "文本模型",
    "视觉模型",
    "图像生成模型",
    "视频生成模型",
    "语音模型",
    "向量模型",
    "知识检索模型",
]


class ZhipuSectionIdParser(HTMLParser):
    """HTML Parser for parsing Zhipu model list page using section ID strategy.

    Strategy 1: Parse using h2/h3 section IDs to identify model categories,
    then extract model names from the first column of tables within each section.
    """

    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_tbody = False
        self.in_tr = False
        self.in_td = False
        self.col_index = -1
        self.current_model_name = ""
        self.capture_text = False

        self.current_category: Optional[str] = None
        self.models_by_category: Dict[str, List[str]] = {}

    def handle_starttag(self, tag, attrs):
        # Check title to determine current model category
        if tag in ["h2", "h3"]:
            attr_dict = dict(attrs)
            section_id = attr_dict.get("id", "")

            # Check if section_id matches known categories or contains "模型"
            if section_id in ZHIPU_CATEGORY_IDS or "模型" in section_id:
                self.current_category = section_id

        if tag == "table":
            self.in_table = True
        elif tag == "tbody":
            self.in_tbody = True
        elif tag == "tr":
            self.in_tr = True
            self.col_index = -1
        elif tag == "td":
            self.in_td = True
            self.col_index += 1
            # We assume model name is in the first column (index 0)
            if self.in_table and self.col_index == 0:
                self.capture_text = True
                self.current_model_name = ""

    def handle_endtag(self, tag):
        if tag == "table":
            self.in_table = False
        elif tag == "tbody":
            self.in_tbody = False
        elif tag == "tr":
            self.in_tr = False
        elif tag == "td":
            self.in_td = False
            if self.capture_text:
                self.capture_text = False

                # If not in valid category, ignore
                if not self.current_category:
                    return

                name = self.current_model_name.strip()
                # Filter out table headers or invalid content
                if name and name != "模型":
                    if self.current_category not in self.models_by_category:
                        self.models_by_category[self.current_category] = []
                    # Avoid duplicate addition in same category
                    if name not in self.models_by_category[self.current_category]:
                        self.models_by_category[self.current_category].append(name)

    def handle_data(self, data):
        if self.capture_text:
            self.current_model_name += data


class ZhipuTableHeaderParser(HTMLParser):
    """HTML Parser for parsing Zhipu model list page using table header strategy.

    Strategy 2: Detect tables by looking for header cells containing "模型" or "Model",
    then extract first column values as model names.
    """

    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_thead = False
        self.in_tbody = False
        self.in_tr = False
        self.in_th = False
        self.in_td = False
        self.col_index = -1
        self.current_text = ""
        self.capture_text = False

        # Track if current table has model header
        self.current_table_has_model_header = False
        self.model_column_index = -1

        self.models: List[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.in_table = True
            self.current_table_has_model_header = False
            self.model_column_index = -1
        elif tag == "thead":
            self.in_thead = True
        elif tag == "tbody":
            self.in_tbody = True
        elif tag == "tr":
            self.in_tr = True
            self.col_index = -1
        elif tag == "th":
            self.in_th = True
            self.col_index += 1
            self.capture_text = True
            self.current_text = ""
        elif tag == "td":
            self.in_td = True
            self.col_index += 1
            # Capture text if this is the model column
            if (
                self.current_table_has_model_header
                and self.col_index == self.model_column_index
            ):
                self.capture_text = True
                self.current_text = ""

    def handle_endtag(self, tag):
        if tag == "table":
            self.in_table = False
            self.current_table_has_model_header = False
            self.model_column_index = -1
        elif tag == "thead":
            self.in_thead = False
        elif tag == "tbody":
            self.in_tbody = False
        elif tag == "tr":
            self.in_tr = False
        elif tag == "th":
            self.in_th = False
            if self.capture_text:
                self.capture_text = False
                text = self.current_text.strip()
                # Check if this header indicates a model column
                if "模型" in text or "Model" in text.lower():
                    self.current_table_has_model_header = True
                    self.model_column_index = self.col_index
        elif tag == "td":
            self.in_td = False
            if self.capture_text:
                self.capture_text = False
                name = self.current_text.strip()
                # Filter out empty or header-like content
                if name and name != "模型" and name.lower() != "model":
                    if name not in self.models:
                        self.models.append(name)

    def handle_data(self, data):
        if self.capture_text:
            self.current_text += data


class FetchZhipu(FetchBase):
    """Zhipu AI model list fetcher with multi-strategy parsing."""

    # Default minimum model threshold for degradation detection
    DEFAULT_MIN_MODEL_THRESHOLD = 5

    def __init__(
        self,
        fallback_models: Optional[List[str]] = None,
        min_model_threshold: int = DEFAULT_MIN_MODEL_THRESHOLD,
    ):
        """Initialize FetchZhipu with configuration.

        Args:
            fallback_models: Optional static list of model IDs to return when
                all parsing strategies fail. If None, an empty list is returned
                on failure.
            min_model_threshold: Minimum expected model count. If fewer models
                are extracted, a warning is logged suggesting possible parsing
                degradation. Default: 5.
        """
        self._fallback_models = fallback_models
        self._min_model_threshold = min_model_threshold

    @property
    def provider(self) -> str:
        return "zhipu"

    def fetch_models(self) -> List[str]:
        """Fetch available model list from Zhipu official documentation page.

        Returns:
            List of model ID strings (flattened from all categories).
            If all parsing strategies fail and a fallback list is configured,
            returns the fallback list. Otherwise returns an empty list.
        """
        try:
            html = self._fetch_html(ZHIPU_MODEL_DOC_URL)

            # Validate structure and log warning if markers are missing
            if not self._validate_structure(html):
                self._log_warning(
                    f"[{self.provider}] HTML structure validation failed: "
                    "expected markers (table, tbody, model-related headings) not found. "
                    "Page structure may have changed."
                )

            categorized, strategy_used = self._extract_model_names(html)
            models = self._flatten_categories(categorized)
            model_count = len(models)

            # All strategies failed - use fallback if configured
            if model_count == 0:
                return self._handle_all_strategies_failed()

            # Log success with strategy name and model count at DEBUG level
            if strategy_used:
                self._log_debug(
                    f"[{self.provider}] Parsing succeeded using strategy '{strategy_used}', "
                    f"extracted {model_count} models"
                )

            # Check for degradation: model count below threshold
            if model_count < self._min_model_threshold:
                self._log_warning(
                    f"[{self.provider}] Model count ({model_count}) is below threshold "
                    f"({self._min_model_threshold}). Possible parsing degradation."
                )

            return models
        except requests.exceptions.RequestException as e:
            self._log_error(
                f"[{self.provider}] HTTP request failed: {e}", exc_info=True
            )
            return self._handle_all_strategies_failed()
        except Exception as e:
            self._log_error(f"[{self.provider}] Unexpected error: {e}", exc_info=True)
            return self._handle_all_strategies_failed()

    def _handle_all_strategies_failed(self) -> List[str]:
        """Handle the case when all parsing strategies fail.

        Returns the fallback list if configured, otherwise returns an empty list.
        Logs appropriate warnings.

        Returns:
            Fallback model list if configured, otherwise empty list.
        """
        if self._fallback_models is not None:
            self._log_warning(
                f"[{self.provider}] All parsing strategies failed. "
                f"Using static fallback list with {len(self._fallback_models)} models."
            )
            return list(self._fallback_models)  # Return a copy to prevent mutation

        return []

    def _flatten_categories(self, categorized: Dict[str, List[str]]) -> List[str]:
        """Flatten categorized model dict into a single list.

        Args:
            categorized: Dict mapping category names to lists of model IDs

        Returns:
            Flattened list containing all model IDs
        """
        result = []
        for models in categorized.values():
            result.extend(models)
        return result

    def _fetch_html(self, url: str) -> str:
        """Request specified URL and return HTML content.

        Uses shared Session from FetchBase for connection reuse.
        The requests library automatically handles gzip/deflate decompression.
        Note: We don't request brotli (br) encoding as it may cause issues
        with some server configurations.
        """
        headers = {"Accept-Encoding": "gzip, deflate"}
        response = self._http_get(url, headers=headers)
        response.raise_for_status()
        return response.text

    def _extract_model_names(
        self, html: str
    ) -> Tuple[Dict[str, List[str]], Optional[str]]:
        """Parse HTML to extract model names using strategy cascade.

        Tries strategies in order: beautifulsoup → section_id → table_headers → pattern.
        Stops on first successful strategy (non-empty result).

        Args:
            html: Raw HTML content from Zhipu documentation page

        Returns:
            Tuple of (Dict mapping category names to lists of model IDs, strategy_name).
            Returns (empty dict, None) if all strategies fail.
        """
        # Strategy 0: BeautifulSoup-based parsing (most robust)
        if HAS_BS4:
            result = self._parse_with_beautifulsoup(html)
            if result:
                return result, "beautifulsoup"

        # Strategy 1: Section ID based parsing (original approach)
        result = self._parse_by_section_id(html)
        if result:
            return result, "section_id"

        # Strategy 2: Table header based parsing
        result = self._parse_by_table_headers(html)
        if result:
            return result, "table_headers"

        # Strategy 3: Pattern-based extraction
        result = self._parse_by_model_pattern(html)
        if result:
            return result, "model_pattern"

        # All strategies failed
        self._log_warning(
            f"[{self.provider}] All parsing strategies failed to extract models"
        )
        return {}, None

    def _parse_with_beautifulsoup(self, html: str) -> Dict[str, List[str]]:
        """Strategy 0: Parse using BeautifulSoup for robust HTML parsing.

        This strategy uses BeautifulSoup to:
        1. Find h3 headings with category IDs (文本模型, 视觉模型, etc.)
        2. Find tables following each heading
        3. Extract model names from the first column of each table

        Args:
            html: Raw HTML content

        Returns:
            Dict mapping category names to lists of model IDs.
            Empty dict if strategy fails to extract any models.
        """
        if not HAS_BS4:
            return {}

        try:
            # Use lxml parser if available, fallback to html.parser
            try:
                soup = BeautifulSoup(html, "lxml")
            except Exception:
                soup = BeautifulSoup(html, "html.parser")

            result: Dict[str, List[str]] = {}

            # Find all h3 headings with known category IDs
            for category_id in ZHIPU_CATEGORY_IDS:
                heading = soup.find(["h2", "h3"], id=category_id)
                if not heading:
                    continue

                # Find the next table after this heading
                # Walk through siblings to find the table
                table = None
                current = heading.find_next_sibling()
                while current:
                    if current.name == "table":
                        table = current
                        break
                    # Also check for table inside a wrapper div
                    if current.name == "div":
                        table = current.find("table")
                        if table:
                            break
                    # Stop if we hit another heading
                    if current.name in ["h2", "h3"]:
                        break
                    current = current.find_next_sibling()

                if not table:
                    continue

                # Extract model names from the first column
                models = []
                tbody = table.find("tbody")
                if tbody:
                    rows = tbody.find_all("tr")
                else:
                    rows = table.find_all("tr")

                for row in rows:
                    cells = row.find_all(["td", "th"])
                    if cells:
                        first_cell = cells[0]
                        # Get text from the cell (may be in an <a> tag)
                        model_name = first_cell.get_text(strip=True)
                        # Filter out header cells
                        if (
                            model_name
                            and model_name != "模型"
                            and model_name.lower() != "model"
                        ):
                            models.append(model_name.lower())

                if models:
                    result[category_id] = models

            # If no models found via category headings, try finding all tables with "模型" header
            if not result:
                result = self._parse_tables_with_model_header(soup)

            return result

        except Exception:
            return {}

    def _parse_tables_with_model_header(
        self, soup: "BeautifulSoup"
    ) -> Dict[str, List[str]]:
        """Parse all tables that have a "模型" or "Model" header column.

        Args:
            soup: BeautifulSoup object

        Returns:
            Dict with models under "unknown" category.
        """
        models = []

        for table in soup.find_all("table"):
            # Check if table has a model header
            headers = table.find_all("th")
            model_col_index = -1

            for i, th in enumerate(headers):
                text = th.get_text(strip=True)
                if "模型" in text or "model" in text.lower():
                    model_col_index = i
                    break

            if model_col_index < 0:
                continue

            # Extract model names from the identified column
            tbody = table.find("tbody")
            if tbody:
                rows = tbody.find_all("tr")
            else:
                rows = table.find_all("tr")

            for row in rows:
                cells = row.find_all("td")
                if len(cells) > model_col_index:
                    cell = cells[model_col_index]
                    model_name = cell.get_text(strip=True)
                    if (
                        model_name
                        and model_name != "模型"
                        and model_name.lower() != "model"
                    ):
                        model_lower = model_name.lower()
                        if model_lower not in models:
                            models.append(model_lower)

        if models:
            return {"unknown": models}
        return {}

    def _parse_by_section_id(self, html: str) -> Dict[str, List[str]]:
        """Strategy 1: Parse using h2/h3 section IDs (current approach).

        Extracts model names by identifying sections with category IDs,
        then parsing tables within those sections.

        Args:
            html: Raw HTML content

        Returns:
            Dict mapping category names to lists of model IDs.
            Empty dict if strategy fails to extract any models.
        """
        parser = ZhipuSectionIdParser()
        try:
            parser.feed(html)
        except Exception:
            return {}

        # Convert model names to lowercase uniformly
        result = {}
        for category, models in parser.models_by_category.items():
            result[category] = [m.lower() for m in models]

        return result

    def _parse_by_table_headers(self, html: str) -> Dict[str, List[str]]:
        """Strategy 2: Parse by detecting table headers containing '模型' or 'Model'.

        Detects tables by looking for header cells containing model-related text,
        then extracts first column values as model names.

        Args:
            html: Raw HTML content

        Returns:
            Dict mapping category names to lists of model IDs.
            Empty dict if no suitable tables found.
        """
        parser = ZhipuTableHeaderParser()
        try:
            parser.feed(html)
        except Exception:
            return {}

        if not parser.models:
            return {}

        # Return models under "unknown" category since we can't determine categories
        # Convert to lowercase for consistency
        return {"unknown": [m.lower() for m in parser.models]}

    def _parse_by_model_pattern(self, html: str) -> Dict[str, List[str]]:
        """Strategy 3: Extract using regex patterns for known model names.

        Scans entire HTML for matches against known Zhipu model name patterns
        (glm-*, chatglm-*, codegeex-*, cogview-*, cogvideo-*, etc.).

        Args:
            html: Raw HTML content

        Returns:
            Dict with models under "unknown" category.
            Empty dict if no patterns match.
        """
        models: List[str] = []
        seen: set = set()

        for pattern in ZHIPU_MODEL_PATTERNS:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                model_lower = match.lower()
                if model_lower not in seen:
                    seen.add(model_lower)
                    models.append(model_lower)

        if not models:
            return {}

        return {"unknown": models}

    def _validate_structure(self, html: str) -> bool:
        """Check if HTML contains expected structural markers.

        Validates that the HTML content has the expected structure for parsing:
        - Contains <table> element
        - Contains <tbody> element
        - Contains headings (h2/h3) with known category IDs or "模型" in content

        Args:
            html: Raw HTML content

        Returns:
            True if all expected markers are present, False otherwise.
        """
        # Check for table element
        has_table = "<table" in html.lower()

        # Check for tbody element
        has_tbody = "<tbody" in html.lower()

        # Check for model-related headings
        # Look for h2/h3 with known category IDs or containing "模型"
        has_model_heading = False

        # Check for known category IDs
        for category_id in ZHIPU_CATEGORY_IDS:
            if f'id="{category_id}"' in html:
                has_model_heading = True
                break

        # Also check for headings containing "模型" in content
        if not has_model_heading:
            has_model_heading = bool(
                re.search(r"<h[23][^>]*>[^<]*模型[^<]*</h[23]>", html)
                or re.search(r">模型</span>", html)  # For span-wrapped text
            )

        return has_table and has_tbody and has_model_heading
