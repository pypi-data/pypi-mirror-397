from mcp.server.fastmcp import FastMCP
from .auth import TokenManager
from .client import ZhongzhiClient
import logging
import json

# Initialize FastMCP
mcp = FastMCP("zhongzhi-mcp")

# Global instances
token_manager = TokenManager()
client = ZhongzhiClient(token_manager)

@mcp.resource("config://status")
def get_status() -> str:
    """Returns the status of the connection."""
    if token_manager.token:
        return "Connected"
    return "Disconnected"

@mcp.tool()
def shunjian_search_patents(
    tm_name: str = None, reg_num: str = None, page: int = 1, page_size: int = 10,
    search_app_name_cn: str = None, app_addr: str = None, search_app_region: str = None,
    search_agent_name: str = None, app_date_start: str = None, app_date_end: str = None,
    search_rights_status: str = None, first_annc_issue: str = None, first_annc_date_start: str = None,
    first_annc_date_end: str = None, reg_annc_issue: str = None, reg_annc_date_start: str = None,
    reg_annc_date_end: str = None, goods_cn_name: str = None, int_cls_search: str = None,
    applicant_type: str = None, similar_code: str = None, search_if_wellknow_tm: str = None,
    app_year: str = None, reg_year: str = None, mode: str = None, sort_field: str = None,
    sort_method: str = None, is_risk: str = None, tm_type: str = None, if_share_tm: str = None,
    if_solid_tm: str = None, if_landmark_info: str = None, priority_num: str = None,
    priority_country: str = None, priority_date_start: str = None, priority_date_end: str = None,
    property_bgn_date_start: str = None, property_bgn_date_end: str = None,
    property_end_date_start: str = None, property_end_date_end: str = None,
    event_name: str = None, process_name: str = None, flow_date_start: str = None,
    flow_date_end: str = None, is_aggs: str = None, aggs: str = None, country_name: str = None
) -> str:
    """
    Search for trademarks/patents using the Zhongzhi API.
    All parameters are optional.

    Args:
        tm_name: Trademark Name
        reg_num: Registration Number
        page: Page number
        page_size: Page size
        search_app_name_cn: Applicant Name
        app_addr: Applicant Address
        search_app_region: Applicant Region (e.g., "Province-City-District")
        search_agent_name: Agent Name
        app_date_start: Application Date Start (YYYY-MM-DD)
        app_date_end: Application Date End (YYYY-MM-DD)
        search_rights_status: Legal Status (待审中,已初审,已注册,已销亡)
        first_annc_issue: First Announcement Issue
        first_annc_date_start: First Announcement Date Start
        first_annc_date_end: First Announcement Date End
        reg_annc_issue: Registration Announcement Issue
        reg_annc_date_start: Registration Announcement Date Start
        reg_annc_date_end: Registration Announcement Date End
        goods_cn_name: Goods/Service Name
        int_cls_search: International Classification
        applicant_type: Applicant Type (0:All, 1:Person, 2:Company)
        similar_code: Similar Group Code
        search_if_wellknow_tm: Is Well-known (0/1)
        app_year: Application Year
        reg_year: Registration Year
        mode: Search Mode (0:Fuzzy, 1:Exact)
        sort_field: Sort Field
        sort_method: Sort Method (asc/desc)
        is_risk: Has Risk Info (0/1)
        tm_type: Trademark Type (P,Z,J,T)
        if_share_tm: Is Shared (0/1)
        if_solid_tm: Is 3D (0/1)
        if_landmark_info: Is Geographical Indication (0/1)
        priority_num: Priority Number
        priority_country: Priority Country
        priority_date_start: Priority Date Start
        priority_date_end: Priority Date End
        property_bgn_date_start: Property Begin Date Start
        property_bgn_date_end: Property Begin Date End
        property_end_date_start: Property End Date Start
        property_end_date_end: Property End Date End
        event_name: Flow Business Name
        process_name: Flow Step Name
        flow_date_start: Flow Date Start
        flow_date_end: Flow Date End
        is_aggs: Is Aggregation (0/1)
        aggs: Aggregation Fields
        country_name: Country Name
    """
    try:
        result = client.search_patents(
            tm_name=tm_name, reg_num=reg_num, page=page, page_size=page_size,
            search_app_name_cn=search_app_name_cn, app_addr=app_addr,
            search_app_region=search_app_region, search_agent_name=search_agent_name,
            app_date_start=app_date_start, app_date_end=app_date_end,
            search_rights_status=search_rights_status, first_annc_issue=first_annc_issue,
            first_annc_date_start=first_annc_date_start, first_annc_date_end=first_annc_date_end,
            reg_annc_issue=reg_annc_issue, reg_annc_date_start=reg_annc_date_start,
            reg_annc_date_end=reg_annc_date_end, goods_cn_name=goods_cn_name,
            int_cls_search=int_cls_search, applicant_type=applicant_type, similar_code=similar_code,
            search_if_wellknow_tm=search_if_wellknow_tm, app_year=app_year, reg_year=reg_year,
            mode=mode, sort_field=sort_field, sort_method=sort_method, is_risk=is_risk,
            tm_type=tm_type, if_share_tm=if_share_tm, if_solid_tm=if_solid_tm,
            if_landmark_info=if_landmark_info, priority_num=priority_num,
            priority_country=priority_country, priority_date_start=priority_date_start,
            priority_date_end=priority_date_end, property_bgn_date_start=property_bgn_date_start,
            property_bgn_date_end=property_bgn_date_end, property_end_date_start=property_end_date_start,
            property_end_date_end=property_end_date_end, event_name=event_name,
            process_name=process_name, flow_date_start=flow_date_start, flow_date_end=flow_date_end,
            is_aggs=is_aggs, aggs=aggs, country_name=country_name
        )
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def shunjian_get_patent_detail(tid: str, detail_type: str = "0") -> str:
    """
    Get details of a specific trademark/patent.
    
    Args:
        tid: The trademark ID (usually the Registration Number / regNum).
        detail_type: The type of detail to retrieve (default "0").
    """
    try:
        result = client.get_patent_detail(tid, detail_type)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def shunjian_get_pledge_info(reg_num: str, int_cls: str, page: int = 1, page_size: int = 10) -> str:
    """
    Get pledge information for a trademark.
    
    Args:
        reg_num: Registration Number.
        int_cls: International Classification.
    """
    try:
        result = client.get_pledge_info(reg_num, int_cls, page, page_size)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def shunjian_get_balance() -> str:
    """
    Get the interface balance.
    """
    try:
        result = client.get_balance()
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def shunjian_image_search(image_url: str) -> str:
    """
    Search for trademarks by image URL.
    """
    try:
        result = client.image_search(image_url)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def shunjian_image_search_aggregation(image_url: str) -> str:
    """
    Search for trademarks by image URL (Aggregation).
    """
    try:
        result = client.image_search_aggregation(image_url)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

@mcp.tool()
def shunjian_check_sensitive_word(word: str) -> str:
    """
    Check if a word is sensitive.
    """
    try:
        result = client.check_sensitive_word(word)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"

# Initialize authentication on startup
try:
    token_manager.start_scheduler()
except Exception as e:
    logging.error(f"Failed to start token manager: {e}")

def main():
    mcp.run()

if __name__ == "__main__":
    main()
