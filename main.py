import moex_broker_toolkit as mbtk
import datetime


if __name__ == "__main__":
    date = datetime.date.today()

    all_stock = mbtk.AllStockInfo(path=r'support_files/rates_all.csv')
    splitter_vtb = mbtk.VtbSplitter()
    splitter_vtb.split(r'.reports/vtb_20251013_20251027.xlsx')
    splitter_sber = mbtk.SberSplitter()
    splitter_sber.split(r'.reports/sber_27102025.html')

    report_registry = mbtk.ReportRegistry()

    vtb_parser = mbtk.VtbPareser(
        all_stock_info=all_stock,
        splitter=splitter_vtb,
        registry=report_registry
    )

    sber_parser = mbtk.SberPareser(
        all_stock_info=all_stock,
        splitter=splitter_sber,
        registry=report_registry
    )

    sber_parser.get_balance_report_df()
    vtb_parser.get_balance_report_df()

    ds = mbtk.DistributionTable(
        r'support_files/index_fund.xlsx', 
        all_stock_info=all_stock
        )
    ds.get_table().to_excel(f'.output/dt_{date}.xlsx', index=False)

    br = mbtk.BalanceReport(
        report_registry=report_registry,
        distribution_table=ds
        )
    br.get_balance_report().to_excel(f'.output/br_{date}.xlsx', index=False)

    ta = mbtk.TargetAllocator(
        distribution_table=ds,
        balance_report=br,
        deposit=44000,
        allow_sell=False,
        tickers_to_sell=['SBMM', 'LQDT']
    )

    df = ta.get_distrib_of_money_df()

    df.to_excel(f'.output/TargetAllocator_{date}.xlsx', index=False)
    print(df)
    print(ta.get_money_count())
    print(ta.work_log)

    rs = mbtk.MdReportStrategy(
        targetAllocator=ta,
        template_path=r'moex_broker_toolkit/templates/md_template.md')
    rg = mbtk.ReportGenerator(rs)
    rg.generate_report()
    
    rg.save_report(f'/Users/ilya/Documents/svlv_storage/SVLV_notebook/00_Notes/broker_report_{date}.md')


