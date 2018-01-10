import os
import re
from dateutil.parser import parse
from collections import defaultdict


def logs_to_line_list():
    log_location = r'C:\Users\nahum-t\Documents\PerfDisPro'
    log_files = [os.path.join(log_location, f) for f in os.listdir(log_location)]
    raw_dispro = []
    for log_file in log_files:
        with file(log_file) as f:
            raw_dispro.extend([LogEntry(l) for l in f])
    return raw_dispro


class LogEntry:
    def __init__(self, log_string):
        try:
            execution_id_search = re.search(r"Execution Id:\s'(\S*)'", log_string)
            command_name_search = re.search(r"Command\s'(\w*)'", log_string)
            command_status_search = re.search(r"Command\s'\w*'\s(\w*),", log_string)
            date_search = re.search(r'^(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3})', log_string)
            self.date = self.GetSearchFirstGroupOrDefault(date_search)
            self.date.replace(',', '.') if self.date else None
            self.date = parse(self.date) if self.date else None
            self.execution_id = self.GetSearchFirstGroupOrDefault(execution_id_search)
            self.command_name = self.GetSearchFirstGroupOrDefault(command_name_search)
            self.command_status = self.GetSearchFirstGroupOrDefault(command_status_search)
            self.started = 'started' in self.command_status.lower() if self.command_status else False
            self.ended = 'completed' in self.command_status.lower() if self.command_status else False
            self.queued = 'queued' in self.command_status.lower() if self.command_status else False

        except Exception as e:
            self.exception = e

    def GetSearchFirstGroupOrDefault(self, search):
        return search.group(1) if search else None

class Execution:
    def __init__(self, log_entries):
        self.log_entries = log_entries
        command_queued_log_entries = [l for l in log_entries if l.queued]
        command_queued_log_entries.sort(key=lambda x: x.date)
        command_started_entries = [l for l in log_entries if l.started]
        command_ended_entries = [l for l in log_entries if l.ended]
        if command_started_entries:
            command_started = command_started_entries[0]
        else:
            return
        if command_ended_entries:
            command_ended = command_ended_entries[0]
        else:
            return
        self.command_name = command_ended.command_name
        self.execution_id = command_ended.execution_id
        first_command_queued = command_queued_log_entries[0] if command_queued_log_entries else None
        if command_ended and command_ended.date and command_started and command_started.date:
            self.duration_from_started_in_milliseconds = (command_ended.date - command_started.date).total_seconds()
        if first_command_queued and first_command_queued.date and command_ended and command_ended.date :
            self.duration_from_queeud_in_milliseconds = (command_ended.date - first_command_queued.date).total_seconds()


def logentries_with_commands():
    grouped_log_entries = defaultdict(list)
    for le in logs_to_line_list():
        if le.execution_id and le.command_status:
            grouped_log_entries[le.execution_id].append(le)
    for k, v in grouped_log_entries.iteritems():
        grouped_log_entries[k] = Execution(v)
    return grouped_log_entries


results = logentries_with_commands()
duration_queued = sorted([(v.duration_from_queeud_in_milliseconds, v.command_name, v.execution_id) for k, v in results.iteritems() if hasattr(v, 'duration_from_queeud_in_milliseconds') and v.command_name=='Deploy'], reverse=True)
duration_from_started = sorted([(v.duration_from_started_in_milliseconds, v.command_name, v.execution_id) for k, v in results.iteritems() if hasattr(v, 'duration_from_started_in_milliseconds') and v.command_name=='Deploy'], reverse=True)


print 'lol'


