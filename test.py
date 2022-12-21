import unittest
from main import getAllTimestamps
from timestamp import Timestamp
class TestGetTimestampRegex(unittest.TestCase):
    
    # Test a single timestamp
    def test_single_timestamp(self):
        output = getAllTimestamps(["$c 02:24-03:45"])
        expectedTimestamp = Timestamp("c", "02","24","03","45")
        
        self.assertEqual(len(output),1)
        self.assertEqual(output[0],expectedTimestamp)
        
    # Test timestamps without leading 0
    def test_timestamp_without_0(self):
        output = getAllTimestamps(["$c 2:24-3:45"])
        expectedTimestamp = Timestamp("c", "2","24","3","45")
        
        self.assertEqual(len(output),1)
        self.assertEqual(output[0],expectedTimestamp)

    # Test multiple timestamps in a singular comment
    def test_multiple_timestamps_single_comment(self):
        output = getAllTimestamps(["$c 2:24-3:45 $s 02:25-03:40"])
        expectedTimestamp1 = Timestamp("c", "2","24","3","45")
        expectedTimestamp2 = Timestamp("s", "2","25","3","40")
        self.assertEqual(len(output),2)
        self.assertEqual(output[0],expectedTimestamp1)
        self.assertEqual(output[1],expectedTimestamp2)
        
    # Test singular timestamps in a multiple comment
    def test_single_timestamp_multiple_comments(self):
        output = getAllTimestamps(["$c 2:24-3:45", "$s 02:25-03:40"])
        expectedTimestamp1 = Timestamp("c", "2","24","3","45")
        expectedTimestamp2 = Timestamp("s", "2","25","3","40")
        self.assertEqual(len(output),2)
        self.assertEqual(output[0],expectedTimestamp1)
        self.assertEqual(output[1],expectedTimestamp2)
        
    # Test timestamps are sorted
    def test_sorted_timestamp(self):
        output = getAllTimestamps(["$f 50:34-55:24", "$c 2:24-3:45 $w 2:26-2:28", "$s 02:25-03:40"])
        
        expectedTimestamp1 = Timestamp("c", "2","24","3","45")
        expectedTimestamp2 = Timestamp("s", "2","25","3","40")
        expectedTimestamp3 = Timestamp("w", "2","26","2","28")
        expectedTimestamp4 = Timestamp("f", "50", "34", "55", "24")

        self.assertEqual(len(output),4)
        self.assertEqual(output[0],expectedTimestamp1)
        self.assertEqual(output[1],expectedTimestamp2)
        self.assertEqual(output[2],expectedTimestamp3)
        self.assertEqual(output[3],expectedTimestamp4)

        
if __name__ == '__main__':
    unittest.main()