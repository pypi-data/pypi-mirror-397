import httpx
import logging
from typing import Optional, Dict, Any
from . import config
from .auth import TokenManager

logger = logging.getLogger(__name__)

class ZhongzhiClient:
    def __init__(self, token_manager: TokenManager):
        self.token_manager = token_manager
        self.client = httpx.Client(timeout=30.0)

    def _get_headers(self) -> Dict[str, str]:
        token = self.token_manager.get_token()
        return {
            "token": token,
            "Content-Type": "application/x-www-form-urlencoded"
        }

    def search_patents(self, 
                       tm_name: Optional[str] = None, 
                       reg_num: Optional[str] = None, 
                       page: int = 1, 
                       page_size: int = 10,
                       # Expanded parameters
                       search_app_name_cn: Optional[str] = None,
                       app_addr: Optional[str] = None,
                       search_app_region: Optional[str] = None,
                       search_agent_name: Optional[str] = None,
                       app_date_start: Optional[str] = None,
                       app_date_end: Optional[str] = None,
                       search_rights_status: Optional[str] = None,
                       first_annc_issue: Optional[str] = None,
                       first_annc_date_start: Optional[str] = None,
                       first_annc_date_end: Optional[str] = None,
                       reg_annc_issue: Optional[str] = None,
                       reg_annc_date_start: Optional[str] = None,
                       reg_annc_date_end: Optional[str] = None,
                       goods_cn_name: Optional[str] = None,
                       int_cls_search: Optional[str] = None,
                       applicant_type: Optional[str] = None,
                       similar_code: Optional[str] = None,
                       search_if_wellknow_tm: Optional[str] = None,
                       app_year: Optional[str] = None,
                       reg_year: Optional[str] = None,
                       mode: Optional[str] = None,
                       sort_field: Optional[str] = None,
                       sort_method: Optional[str] = None,
                       is_risk: Optional[str] = None,
                       tm_type: Optional[str] = None,
                       if_share_tm: Optional[str] = None,
                       if_solid_tm: Optional[str] = None,
                       if_landmark_info: Optional[str] = None,
                       priority_num: Optional[str] = None,
                       priority_country: Optional[str] = None,
                       priority_date_start: Optional[str] = None,
                       priority_date_end: Optional[str] = None,
                       property_bgn_date_start: Optional[str] = None,
                       property_bgn_date_end: Optional[str] = None,
                       property_end_date_start: Optional[str] = None,
                       property_end_date_end: Optional[str] = None,
                       event_name: Optional[str] = None,
                       process_name: Optional[str] = None,
                       flow_date_start: Optional[str] = None,
                       flow_date_end: Optional[str] = None,
                       is_aggs: Optional[str] = None,
                       aggs: Optional[str] = None,
                       country_name: Optional[str] = None,
                       **kwargs) -> Dict[str, Any]:
        """
        Search patents using the customized query interface.
        """
        url = f"{config.BASE_URL}{config.SEARCH_ENDPOINT}"
        data = {
            "page": page,
            "pageSize": page_size
        }
        if tm_name:
            data["tmName"] = tm_name
        if reg_num:
            data["regNum"] = reg_num
        
        # Map python snake_case to API camelCase
        param_map = {
            "searchAppNameCn": search_app_name_cn,
            "appAddr": app_addr,
            "searchAppRegion": search_app_region,
            "searchAgentName": search_agent_name,
            "appDateStart": app_date_start,
            "appDateEnd": app_date_end,
            "searchRightsStatus": search_rights_status,
            "firstAnncIssue": first_annc_issue,
            "firstAnncDateStart": first_annc_date_start,
            "firstAnncDateEnd": first_annc_date_end,
            "regAnncIssue": reg_annc_issue,
            "regAnncDateStart": reg_annc_date_start,
            "regAnncDateEnd": reg_annc_date_end,
            "goodsCnName": goods_cn_name,
            "intClsSearch": int_cls_search,
            "applicantType": applicant_type,
            "similarCode": similar_code,
            "searchIfWellknowTm": search_if_wellknow_tm,
            "appYear": app_year,
            "regYear": reg_year,
            "mode": mode,
            "sortField": sort_field,
            "sortMethod": sort_method,
            "isRisk": is_risk,
            "tmType": tm_type,
            "ifShareTm": if_share_tm,
            "ifSolidTm": if_solid_tm,
            "ifLandmarkInfo": if_landmark_info,
            "priorityNum": priority_num,
            "priorityCountry": priority_country,
            "priorityDateStart": priority_date_start,
            "priorityDateEnd": priority_date_end,
            "propertyBgnDateStart": property_bgn_date_start,
            "propertyBgnDateEnd": property_bgn_date_end,
            "propertyEndDateStart": property_end_date_start,
            "propertyEndDateEnd": property_end_date_end,
            "eventName": event_name,
            "processName": process_name,
            "flowDateStart": flow_date_start,
            "flowDateEnd": flow_date_end,
            "isAggs": is_aggs,
            "aggs": aggs,
            "countryName": country_name
        }
        
        for k, v in param_map.items():
            if v is not None:
                data[k] = v

        data.update(kwargs)
        data = {k: v for k, v in data.items() if v is not None}
        
        try:
            response = self.client.post(url, data=data, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Search error: {e}")
            raise

    def get_patent_detail(self, tid: str, detail_type: str = "0") -> Dict[str, Any]:
        """
        Get patent details using the customized detail interface.
        """
        url = f"{config.BASE_URL}{config.DETAIL_ENDPOINT}"
        params = {
            "tid": tid,
            "type": detail_type
        }
        try:
            response = self.client.get(url, params=params, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Detail error: {e}")
            raise

    def get_pledge_info(self, reg_num: str, int_cls: str, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        """
        Get pledge information.
        """
        url = f"{config.BASE_URL}{config.PLEDGE_ENDPOINT}"
        data = {
            "regNum": reg_num,
            "intCls": int_cls,
            "page": page,
            "pageSize": page_size
        }
        try:
            response = self.client.post(url, data=data, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Pledge info error: {e}")
            raise

    def get_balance(self) -> Dict[str, Any]:
        """
        Get interface balance.
        """
        url = f"{config.BASE_URL}{config.BALANCE_ENDPOINT}"
        try:
            response = self.client.get(url, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Balance error: {e}")
            raise

    def image_search(self, image_url: str) -> Dict[str, Any]:
        """
        Search by image.
        """
        url = f"{config.BASE_URL}{config.IMAGE_SEARCH_ENDPOINT}"
        data = {"imageUrl": image_url}
        try:
            response = self.client.post(url, data=data, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Image search error: {e}")
            raise

    def image_search_aggregation(self, image_url: str) -> Dict[str, Any]:
        """
        Search by image (Aggregation).
        """
        url = f"{config.BASE_URL}{config.IMAGE_SEARCH_AGG_ENDPOINT}"
        data = {"imageUrl": image_url}
        try:
            response = self.client.post(url, data=data, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Image search aggregation error: {e}")
            raise

    def check_sensitive_word(self, word: str) -> Dict[str, Any]:
        """
        Check for sensitive words.
        """
        url = f"{config.BASE_URL}{config.SENSITIVE_WORD_ENDPOINT}"
        params = {"word": word}
        try:
            response = self.client.get(url, params=params, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Sensitive word check error: {e}")
            raise
