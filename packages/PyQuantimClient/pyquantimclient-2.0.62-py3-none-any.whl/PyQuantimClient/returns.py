# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import datetime as dt
from .api import quantim

class returns(quantim):
    def __init__(self, username, password, secretpool, env="pdn", api_url=None):
        super().__init__(username, password, secretpool, env, api_url)

    def get_saa(self, port_id, last_update=True):
        data = {'port_id':port_id, "last_update":last_update}
        try:
            resp = self.api_call('port_saa', method="post", data=data, verify=False)
            port_df = pd.DataFrame(resp)
        except Exception as e:
            resp = {'success':False, 'message':str(e)}
            print(resp)
            port_df = None
        return port_df

    def expected_returns(self, ref_curr, views_df=None, tickers=None, assets=None, horizon_in_months=12, views_fx=None, views_conf=0.75, conf_interv=0.75, median=True, period="monthly", since_date="2008-01-01"):
        '''
        Estimate expected returns.
        '''
        views = views_df.to_dict(orient="records") if views_df is not None else None
        views_fx = views_fx.to_dict() if views_fx is not None else None
        data = {'ref_curr':ref_curr, 'views':views, "views_fx":views_fx, "ref_curr":ref_curr, "tickers":tickers, "assets":assets, "horizon_in_months":horizon_in_months, "views_conf":views_conf, "conf_interv":conf_interv, "median":median, "period":period, "since_date":since_date}
        try:
            resp = self.api_call('expected_returns', method="post", data=data, verify=False)
        except:
            resp = {'success':False, 'message':'Check permissions!'}

        exp_ret, views_df, valid_dates_df = pd.DataFrame(resp['expected_rets']), pd.Series(resp['views_abs']) if resp['views_abs'] is not None else None, pd.Series(resp['valid_dates'])
        return exp_ret, views_df, valid_dates_df
    
    def views_transform(self, ref_curr, gaps_df, optim_assets_df, cons_df=None, since_date="2008-01-01", rets_period="monthly"):
        '''
        Gaps.
        '''
        gaps = gaps_df.to_dict(orient="records")
        optim_assets = optim_assets_df.to_dict(orient="records")
        cons = cons_df.to_dict(orient="records") if cons_df is not None else None

        data = {'ref_curr':ref_curr, 'gaps':gaps, "optim_assets":optim_assets, "cons":cons,
                 "since_date":since_date, "rets_period":rets_period}

        for attempt in range(2):
            try:
                resp = self.api_call('views_transform', method="post", data=data, verify=False)
                break  # success → exit loop
            except Exception as e:
                if attempt == 1:  # last attempt
                    resp = {'success': False, 'message': 'Cannot optimize gaps!', 'error': str(e)}
        if getattr(resp, "status", None) == "error":
            resp = {'success': False, 'message': 'Cannot optimize gaps!', 'error': resp.msg}
        else:
            gaps_consol_df, te_df, invalid_assets, ref_dates = pd.DataFrame(resp['gaps_df']).set_index("Asset"), pd.Series(resp['te']), resp['invalid_assets'], resp['ref_dates']
        return gaps_consol_df, te_df, invalid_assets, ref_dates
