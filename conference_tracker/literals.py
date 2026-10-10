"""Parse a small, data-only subset of JS literals. Never execute remote JS."""
import json
import re


class LiteralParser:
    def __init__(self, text, pos=0):
        self.text, self.pos = text, pos

    def space(self):
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            self.pos += 1

    def take(self, token):
        self.space()
        if not self.text.startswith(token, self.pos):
            raise ValueError(f"Expected {token!r} at offset {self.pos}")
        self.pos += len(token)

    def value(self, depth=0):
        if depth > 30:
            raise ValueError("Literal nesting limit exceeded")
        self.space()
        char = self.text[self.pos:self.pos + 1]
        if char == '"':
            value, length = json.JSONDecoder().raw_decode(self.text[self.pos:])
            self.pos += length
            return value
        if char in ('[', '{'):
            is_object = char == '{'
            end = '}' if is_object else ']'
            out = {} if is_object else []
            self.take(char)
            self.space()
            while not self.text.startswith(end, self.pos):
                if is_object:
                    if self.text[self.pos:self.pos+1] == '"':
                        key = self.value(depth + 1)
                    else:
                        match = re.match(r'[A-Za-z_$][\w$]*', self.text[self.pos:])
                        if not match:
                            raise ValueError("Unsupported object key")
                        key = match[0]
                        self.pos += len(key)
                    self.take(':')
                    if key in out:
                        raise ValueError(f"Duplicate literal key: {key}")
                    out[key] = self.value(depth + 1)
                else:
                    out.append(self.value(depth + 1))
                self.space()
                if self.text.startswith(end, self.pos):
                    break
                self.take(',')
                self.space()
            self.take(end)
            return out
        for token, result in [('!0', True), ('!1', False), ('true', True), ('false', False), ('null', None)]:
            if self.text.startswith(token, self.pos):
                self.pos += len(token)
                return result
        match = re.match(r'-?\d+(?:\.\d+)?', self.text[self.pos:])
        if match:
            self.pos += len(match[0])
            return json.loads(match[0])
        raise ValueError(f"Unsupported JS expression at offset {self.pos}")
