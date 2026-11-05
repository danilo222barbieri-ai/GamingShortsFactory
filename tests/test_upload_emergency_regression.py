import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

class TestUploadEmergencyRegression(unittest.TestCase):
    def test_home_html_has_no_syntax_errors(self):
        """Verify home_v154_component/index.html has balanced brackets, no dangling tokens, no top-level await."""
        home_path = ROOT / "web" / "home_v154_component" / "index.html"
        self.assertTrue(home_path.exists())
        content = home_path.read_text(encoding="utf-8")
        
        # Check that top-level await outside async function does not exist
        # Check that the dangling ghost snippet is gone
        self.assertNotIn("const caps=await capabilities();\n     if(caps&&caps.bucket===true)", content)
        self.assertNotIn("statusText.textContent=\"Upload interrotto — riprova\";", content)
        
        # Count bracket balance in the script tag
        script_start = content.rfind("<script>")
        script_end = content.rfind("</script>")
        self.assertGreater(script_start, 0)
        self.assertGreater(script_end, script_start)
        
        js_code = content[script_start + len("<script>"):script_end]
        
        # Clean strings and comments to verify bracket balancing
        chars = []
        in_str = None
        in_line_comment = False
        in_block_comment = False
        i = 0
        n = len(js_code)
        while i < n:
            ch = js_code[i]
            nxt = js_code[i+1] if i + 1 < n else ""
            if in_str:
                if ch == "\\" and in_str != "`":
                    i += 2
                    continue
                elif ch == in_str:
                    in_str = None
            elif in_line_comment:
                if ch == "\n":
                    in_line_comment = False
            elif in_block_comment:
                if ch == "*" and nxt == "/":
                    in_block_comment = False
                    i += 1
            else:
                if ch in ('"', "'", "`"):
                    in_str = ch
                elif ch == "/" and nxt == "/":
                    in_line_comment = True
                    i += 1
                elif ch == "/" and nxt == "*":
                    in_block_comment = True
                    i += 1
                elif ch in "{}()[]":
                    chars.append((ch, i))
            i += 1

        pairs = {')': '(', '}': '{', ']': '['}
        stack = []
        for ch, pos in chars:
            if ch in "({[":
                stack.append((ch, pos))
            elif ch in ")}]":
                self.assertTrue(len(stack) > 0, f"Unmatched closing '{ch}' at character position {pos}")
                expected = pairs[ch]
                actual, _ = stack.pop()
                self.assertEqual(actual, expected, f"Mismatched bracket '{actual}' vs closing '{ch}' at position {pos}")
        self.assertEqual(len(stack), 0, f"Unclosed brackets remain: {stack}")

    def test_social_sid_cookie_fallback(self):
        """Verify _social_sid in direct_upload_server extracts session from cookie when header is absent."""
        orig_sys_path = list(sys.path)
        try:
            web_path = str(ROOT / "web")
            if web_path not in sys.path:
                sys.path.insert(0, web_path)
            import direct_upload_server as dus
            _social_sid = dus._social_sid
            
            class MockHandler:
                def __init__(self, headers):
                    self.headers = headers
                    
            # Case 1: header present
            h1 = MockHandler({"X-GSF-Session-ID": "sess_hdr_1234567890abcdef"})
            self.assertEqual(_social_sid(h1), "sess_hdr_1234567890abcdef")
            
            # Case 2: header absent, cookie present
            h2 = MockHandler({"Cookie": "other_pref=dark; gsf_sid=sess_cookie_1234567890abcdef; lang=it"})
            self.assertEqual(_social_sid(h2), "sess_cookie_1234567890abcdef")
            
            # Case 3: neither present
            h3 = MockHandler({})
            self.assertEqual(_social_sid(h3), "")
        finally:
            sys.path[:] = orig_sys_path

if __name__ == "__main__":
    unittest.main()
