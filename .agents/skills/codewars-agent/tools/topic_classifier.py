import re

class TopicClassifier:
    """Masalalarni haqiqiy Python dasturlash mavzulari bo'yicha chuqur tahlil qilish va tasniflash vositasi."""

    TOPIC_RULES = {
        'oop': {
            'tags': ['object-oriented programming', 'oop'],
            'keywords': ['class ', 'class:', '__init__', 'inheritance', 'instance', 'self.', 'method', 'polymorphism', 'subclass'],
            'display_name': 'Object-Oriented Programming (OOP)'
        },
        'regular_expressions': {
            'tags': ['regular expressions', 'regex'],
            'keywords': ['regex', 'regexp', 'regular expression', 're.match', 're.search', 're.sub', 're.findall', 'pattern matching'],
            'display_name': 'Regular Expressions (Regex)'
        },
        'while_loop': {
            'tags': [],
            'keywords': [
                'while', 'until', 'repeat until', 'as long as', 'steps until', 'number of steps',
                'bounces until', 'collatz', 'keep dividing', 'divisible by 7', 'until only', 'reaches zero',
                'population', 'how many years', 'how many days', 'simulation', 'halving', 'shrink',
                'cardinals through sets', 'tower bouncing', 'no zeros for heroes'
            ],
            'display_name': 'While Loop'
        },
        'for_loop': {
            'tags': [],
            'keywords': [
                'for loop', 'for each', 'range(', 'iterate over', 'iteration', 'draw stairs',
                'multiplication table', 'repeat times', 'every second element', 'step through',
                'sum of cubes', 'count the digit', 'multiples of', 'sum of all multiples',
                'sum from 1 to', 'factorial', 'times table', 'print a pattern', 'pyramid', 'staircase',
                'sum of odd numbers', 'sum of numbers', 'consecutive', 'sum of digits', 'parameter of number',
                'counting in the  amazon', 'summing  a number'
            ],
            'display_name': 'For Loop'
        },
        'string': {
            'tags': ['strings'],
            'keywords': [
                'string', 'substring', 'character', 'uppercase', 'lowercase', 'split', 'join',
                'replace', 'slice', 'palindrome', 'vowel', 'consonant', 'ascii', 'word', 'sentence',
                'whitespace', 'pig latin', 'phone number', 'exclamation', 'user links', 'switcheroo',
                'password', 'nickname', 'digits explosion', 'pin code', 'c.wars', 'sayhello', 'find the position'
            ],
            'display_name': 'String (Satrlar)'
        },
        'dictionary': {
            'tags': ['hashmaps'],
            'keywords': ['dictionary', 'dict', 'key-value', 'hashmap', 'keys()', 'values()', 'items()', 'lookup table', 'return to sanity', 'switch/case', 'planet name', 'rumor'],
            'display_name': 'Dictionary (Lug\'atlar)'
        },
        'list': {
            'tags': ['arrays', 'lists'],
            'keywords': [
                'array', 'list of', 'sub-array', 'indices', 'append', 'indexing', 'elements in',
                'list comprehension', 'filter array', 'map array', 'matrix', 'vector', 'coding meetup'
            ],
            'display_name': 'List (Ro\'yxatlar)'
        },
        'algorithms': {
            'tags': ['algorithms', 'sorting'],
            'keywords': [
                'algorithm', 'fibonacci', 'prime number', 'factor', 'recursion', 'recursive', 'binary search',
                'sort', 'sorted', 'bubble sort', 'quick sort', 'order by', 'ascending', 'descending', 'factorial',
                'descending order', 'sieve', 'graph', 'tree'
            ],
            'display_name': 'Algorithms & Sorting'
        },
        'built_in': {
            'tags': [],
            'keywords': [
                'len(', 'min(', 'max(', 'sum(', 'abs(', 'round(', 'type(', 'int(', 'float(', 'str(',
                'decimal places', 'precision', 'format(', 'datetime', 'calendar', 'math.'
            ],
            'display_name': 'Built-in Funksiyalar'
        },
        'if_related_homework': {
            'tags': [],
            'keywords': [
                'if ', 'if/', 'elif', 'else', 'condition', 'conditional', 'check whether', 'check if',
                'ticket', 'grade', 'traffic light', 'umbrella', 'rock paper scissors', 'leap year',
                'decide whether', 'quadrant', 'triangle', 'drink', 'combat', 'secret message',
                'compare numbers', 'real floor', 'alternating', 'dalmatians', 'opposites attract', 'survive',
                'return the day', 'return negative', 'tip calculator'
            ],
            'display_name': 'If / Else Shartlari'
        },
        'logics': {
            'tags': ['logic'],
            'keywords': ['boolean', 'true or false', 'truth table', 'logical and', 'logical or', 'negation', 'xor'],
            'display_name': 'Logics (Mantiq)'
        },
        'arithmetic_operators': {
            'tags': ['mathematics', 'algebra', 'geometry', 'binary'],
            'keywords': [
                'multiply', 'divide', 'addition', 'subtraction', 'modulo', 'remainder', 'power of',
                'arithmetic', 'ratio', 'area of', 'volume of', 'perimeter', 'surface', 'hypotenuse',
                'square of', 'cube of', 'minutes to hours', 'calculate the sum', 'bitwise', 'bit shift',
                'circle of numbers', 'cockroach', 'mangoes', 'double the integer', 'angle', 'basic function fixer',
                'messi goals', 'wrapping paper', 'ratios', 'time convert', 'elapsed seconds', 'reverse the bits',
                'incorrect division', 'how many times should i go', 'get decimal part'
            ],
            'display_name': 'Arithmetic Operators'
        }
    }

    @classmethod
    def classify(cls, name="", tags=None, description=""):
        """Masalaning sharti, teglari va nomini chuqur tahlil qilib, aniq dasturlash mavzusiga ajratadi."""
        tags_lower = [t.lower().strip() for t in (tags or [])]
        text = f"{name} {description}".lower()
        nl = name.lower()

        # 1. OOP (Class, __init__, method, inheritance)
        if 'object-oriented programming' in tags_lower or 'oop' in tags_lower or re.search(r'\bclass\s+\w+', text) or '__init__' in text:
            return 'oop'

        # 2. Regex
        if 'regular expressions' in tags_lower or re.search(r'\bregex\b|\bregexp\b|\bregular expression[s]?\b|\bre\.(match|search|sub|findall|compile)\b', text):
            return 'regular_expressions'

        # 3. Pure While Loop (problems genuinely solved via while loop simulation/reduction)
        while_titles = [
            'growth of a population', 'collatz conjecture', 'money, money, money',
            'bouncing ball', 'tower bouncing', 'a rule of divisibility by 7',
            'no zeros for heroes', 'persistent bugger', 'palindrome chain length',
            'single digit', 'build a pile of cubes', 'coloured triangles',
            'cardinals through sets', 'deodorant evaporator', 'snail crawls up',
            'digital root', 'vexing vanishing values'
        ]
        if any(t in nl for t in while_titles):
            return 'while_loop'
        if re.search(r'repeat(?:ing)? (?:the )?process until|repeat until (?:only|the number)|as long as (?:the|it|you)|until (?:it|the number) reaches zero|until (?:it is|only) a single digit|while loop\b', text):
            if not any(k in nl for k in ['hoop', 'wall', 'sheep', 'goose', 'how old', 'twice as old', 'reverse every', 'candy', 'average', 'odd ladder']):
                return 'while_loop'

        # 4. Pure For Loop (explicit iterations over ranges, step counts, multiplication tables, drawing stairs)
        for_titles = [
            'sum of cubes', 'count the digit', 'multiplication table', 'draw stairs',
            'sum of a sequence', 'sum of numbers from 0 to n', 'complete the pattern #6',
            'summing  a number', 'counting in the  amazon', 'parameter of number',
            'squares sequence', 'build a square'
        ]
        if any(t in nl for t in for_titles):
            return 'for_loop'
        for_patterns = [
            r'\bfor loop\b', r'\brange\(', r'iterate over', r'for each', r'repeat \d+ times',
            r'multiples of', r'sum of all multiples', r'sum from 1 to', r'times table',
            r'print a pattern', r'pyramid', r'staircase', r'consecutive'
        ]
        if any(re.search(p, text) for p in for_patterns):
            if not any(k in nl for k in ['sheep', 'hoop', 'wall', 'goose', 'how old', 'twice as old', 'candy', 'is n divisible']):
                return 'for_loop'

        # 5. String Manipulation
        if 'strings' in tags_lower or re.search(r'\bstring[s]?\b|\bcharacter[s]?\b|\bsubstring\b|\buppercase\b|\blowercase\b|\bpalindrome\b|\bvowel[s]?\b|\bconsonant[s]?\b|\bwords?\b|\bsentence\b|\bascii\b|\bformatting\b|\btext\b|\broman\b|\banagram\b|\bwhitespace\b|\bpig latin\b|\bphone number\b|\bexclamation\b|\buser links\b|\bswitcheroo\b|\bpassword\b|\bnickname\b|\bdigits explosion\b|\bvalidation\b|\bpin code\b|\bc\.wars\b|sayhello|find the position|pay for the wall|reverse every other word', text):
            return 'string'

        # 6. Dictionary
        if re.search(r'\bdict\b|\bdictionary\b|key-value|\bhashmap\b|lookup table|\bkeys\(\)|\bvalues\(\)|return to sanity|\bswitch/case\b|\bplanet name\b|\bmap\b|\brumor\b', text):
            return 'dictionary'

        # 7. List / Array
        if 'arrays' in tags_lower or 'lists' in tags_lower or re.search(r'\barray[s]?\b|\blist[s]?\b|sub-array|\bindic(?:es|ex)\b|\bappend\b|\belements in\b|list comprehension|\bvector\b|\bmatrix\b|coding meetup|developers coming from|counting sheep|duck duck goose|candy problem|average scores|plastic balance|bingo \( or not \)', text):
            return 'list'

        # 8. Algorithms & Sorting
        if 'sorting' in tags_lower or 'algorithms' in tags_lower or re.search(r'\bsort(?:ed|ing)?\b|fibonacci|prime number|\brecursion\b|\brecursive\b|binary search|descending order|sieve|graph|tree|sort the odd|sort out the men', text):
            return 'algorithms'

        # 9. Built-in functions
        if re.search(r'\blen\(|\bmin\(|\bmax\(|\bsum\(|\babs\(|\bround\(|\btype\(|\bint\(|\bfloat\(|\bstr\(|decimal places?|precision|\bmath\.', text):
            return 'built_in'

        # 10. If / Else conditions & branching
        if re.search(r'\bif\b|\belif\b|\belse\b|condition|decide whether|check whether|check if|ticket|grade|traffic light|umbrella|rock paper scissors|leap year|drink|combat|secret message|compare numbers|real floor|alternating|dalmatians|opposites attract|survive|agree|negative zero|tip calculator|return the day|return negative|keep up the hoop|how old will i be', text):
            return 'if_related_homework'

        # 11. Logics (Booleans)
        if 'logic' in tags_lower or re.search(r'\bboolean\b|true or false|truth table|logical and|logical or|\bnegation\b|\bxor\b', text):
            return 'logics'

        # 12. Arithmetic Operators (Math calculations, geometry formulas)
        if 'mathematics' in tags_lower or 'algebra' in tags_lower or 'geometry' in tags_lower or re.search(r'multiply|divide|addition|subtraction|modulo|remainder|power of|arithmetic|ratio|area of|volume of|perimeter|surface|hypotenuse|square of|cube of|minutes to hours|calculate the sum|bitwise|bit shift|circle of numbers|cockroach|mangoes|double the integer|angle|basic function fixer|messi goals|wrapping paper|ratios|time convert|elapsed seconds|reverse the bits|incorrect division|how many times should i go|get decimal part|is n divisible|twice as old|cats in hats', text):
            return 'arithmetic_operators'

        return 'fundamentals_umumiy'

    @classmethod
    def matches_target(cls, target_topic, name="", tags=None, description=""):
        """Masala foydalanuvchi so'ragan mavzuga to'g'ri kelishini tekshiradi."""
        target_norm = target_topic.strip().lower().replace(' ', '_')
        assigned = cls.classify(name=name, tags=tags, description=description)
        return assigned == target_norm

    @staticmethod
    def get_difficulty(rank_str):
        """Kyu darajasini Basic yoki Advanced ga ajratadi."""
        r = str(rank_str).lower()
        if any(k in r for k in ['8 kyu', '7 kyu']):
            return 'Basic'
        if any(k in r for k in ['6 kyu', '5 kyu', '4 kyu', '3 kyu', '2 kyu', '1 kyu']):
            return 'Advanced'
        return 'Basic'
