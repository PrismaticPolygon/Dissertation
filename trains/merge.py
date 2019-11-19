import os
import json
import csv
import time

fields = {
    "0001": ["schedule_source", "train_file_address", "schedule_end_date", "train_id", "tp_origin_timestamp",
             "creation_timestamp", "tp_origin_stanox", "origin_dep_timestamp", "train_service_code", "toc_id",
             "d1266_record_number", "train_call_type", "train_uid", "train_call_mode", "schedule_type",
             "sched_origin_stanox", "schedule_wtt_id", "schedule_start_date"],
    "0002": ["train_file_address","train_service_code", "orig_loc_stanox", "toc_id", "dep_timestamp", "division_code",
             "loc_stanox", "canx_timestamp", "canx_reason_code", "train_id", "orig_loc_timestamp", "canx_type"],
    "0003": ["event_type", "gbtt_timestamp", "original_loc_stanox", "planned_timestamp", "timetable_variation",
             "original_loc_timestamp", "current_train_id", "delay_monitoring_point", "next_report_run_time",
             "reporting_stanox", "actual_timestamp", "correction_ind", "event_source", "train_file_address", "platform",
             "division_code", "train_terminated", "train_id", "offroute_ind", "variation_status", "train_service_code",
             "toc_id", "loc_stanox", "auto_expected", "direction_ind", "route", "planned_event_type",
             "next_report_stanox", "line_ind"],
    "0005": ["current_train_id", "original_loc_timestamp", "train_file_address", "train_service_code", "toc_id",
             "dep_timestamp", "division_code", "loc_stanox", "train_id", "original_loc_stanox",
             "reinstatement_timestamp"],
    "0006": ["reason_code", "current_train_id", "original_loc_timestamp", "train_file_address", "train_service_code",
             "toc_id", "dep_timestamp", "coo_timestamp", "division_code", "loc_stanox", "train_id",
             "original_loc_stanox"],
    "0007": ["current_train_id", "train_file_address", "train_service_code", "revised_train_id", "train_id",
             "event_timestamp"],
    "0008": ["original_loc_timestamp", "current_train_id", "train_file_address", "train_service_code", "dep_timestamp",
             "loc_stanox", "train_id", "original_loc_stanox", "event_timestamp"]
}

def merge():

    in_dir = "extracted"
    out_dir = "data"

    if not os.path.exists(out_dir):

        os.mkdir(out_dir)

    files = {key: open(os.path.join(out_dir, key + ".csv"), "w", newline="") for key in fields.keys()}
    writers = {key: csv.writer(file) for key, file in files.items()}

    for key, writer in writers.items():

        writer.writerow(fields[key])

    for date in os.listdir(in_dir):

        start = time.time()

        print("Merging " + date + "...", end="")

        def parse(messages):

            for message in messages:

                key = message["header"]["msg_type"]

                writers[key].writerow(message["body"].values())

        for file in os.listdir(os.path.join(in_dir, date)):

            path = os.path.join(in_dir, date, file)

            with open(path) as in_file:

                for line in in_file.readlines():

                    line = line.rstrip("\x00")  # Remove trailing null characters

                    try:

                        messages = json.loads(line)

                        parse(messages)

                    except json.decoder.JSONDecodeError as e:

                        print("\nCorrecting JSON error in {}... ".format(path), end="")

                        char = int(str(e).split(" ")[-1][:-1])

                        # Sometimes multiple JSON arrays are erroneously on the same line

                        if line[:char].strip() != "":

                            parse(json.loads(line[char:]))

                        if line[:char].strip() != "":

                            parse(json.loads(line[:char]))

        print("DONE ({:.2f}s)".format(time.time() - start))

    for file in files.values():

        file.close()

    print("")