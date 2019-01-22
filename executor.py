import sys
import multiprocessing

import fuzzer

# https://wiki.wdf.sap.corp/wiki/display/FXU/BRQ3
ODATA_SERVICES = [
    'FAA_ASSET_OVERVIEWPAGE_SRV',
    'FAC_REVENUE_VARIANCE_SRV',
    'FAR_BAD_DEBT_RESERVE_SRV',
    'FAR_BAD_DEBT_RESERVE_SRV',
    'FAR_DISP_PAYMENT_CARD_DATA_SRV',
    'FAR_DOUBTFUL_ACCTS_VALUATION_SRV',
    'FAR_INSPECT_ITEMS_CHNGLOG_SRV',
    'FCO_COST_CENTER_CHNGLOG_SRV',
    'FCO_REALTIME_WIP_REPORTING_SRV',
    'FCO_SALES_ACCTG_OVERVIEW_SRV',
]


def main():
    global_arguments = sys.argv[1:]
    system_url = extract_system_url(global_arguments)

    processes = []
    for odata_service in ODATA_SERVICES:
        arguments = global_arguments + ['-l', odata_service, '-s', odata_service] \
                    + [system_url.rstrip('/') + '/' + odata_service]
        fuzzer_process = multiprocessing.Process(target=fuzzer.execute, args=[arguments])
        fuzzer_process.start()
        processes.append(fuzzer_process)

    for process in processes:
        process.join()


def extract_system_url(global_arguments):
    url_position = 0
    for argument in global_arguments:
        if argument == '-U':
            break
        url_position += 1
    system_url = global_arguments.pop(url_position + 1)
    global_arguments.pop(url_position)
    return system_url


if __name__ == '__main__':
    main()
