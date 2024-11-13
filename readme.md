# Flow Log Parser

A Python program to analyze flow logs and map ports to tags based on a lookup table.

## Overview

This program processes network flow logs and tags each entry based on destination port and protocol combinations defined in a lookup table.

## Requirements

- Python 3.6 or higher
- No additional packages required

## Assumptions and Limitations

### Flow Log Format
- Only supports **default VPC flow log format (Version 2)**
- Each log entry must contain exactly 15 space-separated fields
- Fields must be in this order:
  ```
  version account-id interface-id srcaddr dstaddr srcport dstport protocol packets bytes start end action log-status
  ```
- Protocol numbers supported:
  * 6 = TCP
  * 17 = UDP (though not present in sample data)

### Lookup Table Format
- Must be a CSV file with exactly 3 columns:
  * dstport (destination port number)
  * protocol (tcp/udp)
  * tag (string identifier)
- First row must contain headers
- Port numbers must be between 0-65535
- Protocol must be either 'tcp' or 'udp' (case insensitive)

### Processing Rules
- Matches are case-insensitive for protocols
- Unmatched entries are counted as 'Untagged'
- Each log line contributes to exactly one tag count
- All destination port/protocol combinations are counted, regardless of tag matches

## Usage

1. Prepare your input files:
   - `lookup_table.csv`: Tag definitions
   - `flow_logs.txt`: Flow log data

2. Run the program:
   ```bash
   python flow_log_parser.py
   ```

3. Check the output in `analysis_results.csv`

## Input File Examples

### lookup_table.csv
```csv
dstport,protocol,tag 
25,tcp,sv_P1
68,udp,sv_P2
23,tcp,sv_P1
...
```

### flow_logs.txt
```
2 123456789012 eni-0a1b2c3d 10.0.1.201 198.51.100.2 443 49153 6 25 20000 1620140761 1620140821 ACCEPT OK
2 123456789012 eni-4d3c2b1a 192.168.1.100 203.0.113.101 23 49154 6 15 12000 1620140761 1620140821 REJECT OK
...
```

## Output Format

The program generates `analysis_results.csv` with two sections:

1. Tag Counts:
   ```
   Tag Counts:
   Tag,Count
   sv_P2,1
   sv_P1,2
   email,3
   Untagged,8
   ```

2. Port/Protocol Combinations:
   ```
   Port/Protocol Combination Counts:
   Port,Protocol,Count
   23,tcp,1
   25,tcp,1
   110,tcp,1
   ...
   ```

## Testing

The program was tested with:
1. Sample data provided in the problem statement
2. Edge cases including:
   - Empty lines in flow logs
   - Invalid port numbers
   - Missing fields in log entries
   - Case variations in protocols
   - Non-existent input files
   - Invalid CSV formats

## Error Handling

The program handles several error conditions:
- Missing or unreadable input files
- Invalid CSV format in lookup table
- Invalid flow log format
- Invalid port numbers
- Invalid protocols
- File write permission issues

## Future Improvements

Potential enhancements could include:
1. Support for custom flow log formats
2. Command-line arguments for file paths
3. Parallel processing for large log files
4. More detailed statistics and analysis
5. Support for multiple lookup tables

## Known Issues

1. Program assumes flow log version 2 format only

