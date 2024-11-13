import csv
from collections import defaultdict
import os

class FlowLogParser:
    def __init__(self):
        self.tag_mappings = {}
        self.tag_counts = defaultdict(int)
        self.port_protocol_counts = defaultdict(int)

    def load_lookup_table(self, lookup_file: str) -> None:
        """Load the lookup table from CSV file."""
        try:
            if not os.path.exists(lookup_file):
                raise FileNotFoundError(f"Lookup table file not found: {lookup_file}")

            with open(lookup_file, 'r') as f:
                reader = csv.DictReader(f)
                # Validate headers
                if not {'dstport', 'protocol', 'tag'}.issubset(set(reader.fieldnames or [])):
                    raise ValueError("CSV file must have dstport, protocol, and tag columns")

                for row in reader:
                    key = (row['dstport'], row['protocol'].lower())
                    self.tag_mappings[key] = row['tag']
        except csv.Error as e:
            raise ValueError(f"Invalid CSV format: {str(e)}")

    def get_tag_for_port_protocol(self, port: str, protocol: str) -> str:
        """Get tag for given port and protocol combination."""
        key = (port, protocol)
        return self.tag_mappings.get(key, 'Untagged')

    def process_flow_logs(self, log_file: str) -> None:
        """Process the flow logs file."""
        try:
            if not os.path.exists(log_file):
                raise FileNotFoundError(f"Flow log file not found: {log_file}")

            with open(log_file, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    if not line.strip():
                        continue

                    parts = line.strip().split()
                    if len(parts) < 14:
                        print(f"Warning: Skipping invalid line {line_num}: Insufficient fields")
                        continue

                    try:
                        # Extract ports and protocol
                        dst_port = parts[6]
                        protocol = 'tcp' if parts[7] == '6' else 'udp'

                        # Validate port number
                        if not (dst_port.isdigit() and 0 <= int(dst_port) <= 65535):
                            print(f"Warning: Invalid port number on line {line_num}")
                            continue

                        # Process destination port
                        tag = self.get_tag_for_port_protocol(dst_port, protocol)
                        self.port_protocol_counts[(dst_port, protocol)] += 1
                        if tag != 'Untagged':
                            self.tag_counts[tag] += 1

                    except IndexError:
                        print(f"Warning: Invalid line format at line {line_num}")
                        continue

                # Calculate untagged count
                total_lines = line_num
                tagged_sum = sum(self.tag_counts.values())
                self.tag_counts['Untagged'] = total_lines - tagged_sum

        except Exception as e:
            raise RuntimeError(f"Error processing flow logs: {str(e)}")

    def write_output(self, output_file: str) -> None:
        """Write the analysis results to output file."""
        try:
            with open(output_file, 'w', newline='') as f:
                # Write tag counts
                f.write("Tag Counts:\n")
                f.write("Tag,Count\n")

                sorted_tags = sorted(
                    self.tag_counts.items(),
                    key=lambda x: (-x[1], x[0])
                )

                for tag, count in sorted_tags:
                    if count > 0:
                        f.write(f"{tag},{count}\n")

                # Write port/protocol counts
                f.write("\nPort/Protocol Combination Counts:\n")
                f.write("Port,Protocol,Count\n")

                sorted_ports = sorted(
                    self.port_protocol_counts.items(),
                    key=lambda x: int(x[0][0]) if x[0][0].isdigit() else 0
                )

                for (port, protocol), count in sorted_ports:
                    f.write(f"{port},{protocol},{count}\n")

        except IOError as e:
            raise RuntimeError(f"Error writing to output file: {str(e)}")


def main():
    try:
        # Input files
        lookup_file = 'lookup_table.csv'
        log_file = 'flow_logs.txt'
        output_file = 'analysis_results.csv'

        # Create and run parser
        parser = FlowLogParser()

        try:
            parser.load_lookup_table(lookup_file)
        except (FileNotFoundError, ValueError) as e:
            print(f"Error loading lookup table: {str(e)}")
            return

        try:
            parser.process_flow_logs(log_file)
        except (FileNotFoundError, RuntimeError) as e:
            print(f"Error processing flow logs: {str(e)}")
            return

        try:
            parser.write_output(output_file)
        except RuntimeError as e:
            print(f"Error writing output: {str(e)}")
            return

        print("Processing completed successfully")

    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    main()