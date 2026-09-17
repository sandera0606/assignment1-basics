count = 0
limit = 1000
marker = "<|endoftext|>"

with open("data/TinyStoriesV2-GPT4-train.txt", "r", encoding="utf-8") as infile, open("data/TinyStoriesSubset.txt", "w", encoding="utf-8") as outfile:
    for line in infile:
        # Count how many times the marker appears in this specific line
        marker_cnt = line.count(marker)
        
        if count + marker_cnt >= limit:
            # Find the exact position of the final allowed marker
            remaining_needed = limit - count
            parts = line.split(marker)
            # Reconstruct the line up to the exact included marker
            last_part = marker.join(parts[:remaining_needed]) + marker
            outfile.write(last_part)
            break
        else:
            outfile.write(line)
            count += marker_cnt