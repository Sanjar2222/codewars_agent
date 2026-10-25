import re
import time
import requests

class CodewarsClient:
    """Codewars API va qidiruv tizimi bilan ishlovchi mijoz."""
    
    BASE_API = "https://www.codewars.com/api/v1"
    SEARCH_URL = "https://www.codewars.com/kata/search/python"
    HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CodewarsAgent/1.0"}

    def __init__(self, request_delay=0.3):
        self.delay = request_delay
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def get_user_completed_katas(self, username):
        """Foydalanuvchi ishlagan barcha masalalar ro'yxatini yuklaydi."""
        print(f"[*] Codewars API: @{username} ishlagan masalalari yuklanmoqda...")
        page = 0
        all_katas = []
        
        while True:
            url = f"{self.BASE_API}/users/{username}/code-challenges/completed?page={page}"
            try:
                resp = self.session.get(url, timeout=15)
                if resp.status_code == 404:
                    print(f"[X] Foydalanuvchi @{username} topilmadi!")
                    break
                if resp.status_code == 429:
                    print(f"[!] Rate limit (429), 3 soniya kutilmoqda...")
                    time.sleep(3)
                    continue
                if resp.status_code != 200:
                    print(f"[!] API javob kodi: {resp.status_code}, yuklash to'xtatildi.")
                    break
                    
                data = resp.json()
                items = data.get('data', [])
                if not items:
                    break
                    
                for it in items:
                    all_katas.append({
                        'id': it.get('id'),
                        'name': it.get('name'),
                        'slug': it.get('slug'),
                        'completed_languages': it.get('completedLanguages', []),
                        'completed_at': it.get('completedAt', '')[:10]
                    })
                page += 1
                time.sleep(self.delay)
            except Exception as e:
                print(f"[!] Masalalarni yuklashda xatolik (sahifa {page}): {e}")
                break
                
        print(f"[✓] Jami {len(all_katas)} ta ishlangan masala yuklandi.")
        return all_katas

    def get_kata_details(self, kata_id_or_slug):
        """Aynan bitta masalaning to'liq ma'lumotlarini (description, tags, rank) oladi."""
        url = f"{self.BASE_API}/code-challenges/{kata_id_or_slug}"
        for attempt in range(3):
            try:
                resp = self.session.get(url, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    rank_info = data.get('rank', {})
                    rank_name = rank_info.get('name', '') if rank_info else ''
                    return {
                        'id': data.get('id'),
                        'name': data.get('name'),
                        'slug': data.get('slug'),
                        'url': data.get('url', f"https://www.codewars.com/kata/{data.get('id')}"),
                        'rank': rank_name,
                        'tags': data.get('tags', []),
                        'description': data.get('description', ''),
                        'languages': data.get('languages', [])
                    }
                elif resp.status_code == 429:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                else:
                    break
            except Exception:
                time.sleep(1)
        return None

    def get_katas_details_bulk(self, kata_ids, max_workers=10):
        """Ko'p sonli masalalarning to'liq ma'lumotlarini parallel (tezkor) yuklaydi."""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        print(f"[*] {len(kata_ids)} ta masala ma'lumotlari parallel yuklanmoqda ({max_workers} ta worker)...")
        results = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_id = {executor.submit(self.get_kata_details, pid): pid for pid in kata_ids}
            done_count = 0
            for future in as_completed(future_to_id):
                pid = future_to_id[future]
                try:
                    res = future.result()
                    if res:
                        results[pid] = res
                except Exception:
                    pass
                done_count += 1
                if done_count % 50 == 0 or done_count == len(kata_ids):
                    print(f"   Yuklandi: {done_count}/{len(kata_ids)}...")
        print(f"[✓] Parallel yuklash yakunlandi: {len(results)}/{len(kata_ids)} ta masala olindi.")
        return results

    def search_katas(self, topic_query, kyu_level=None, max_pages=5):
        """Codewars'dan berilgan mavzu va daraja bo'yicha FAQAT Python masalalarini qidiradi."""
        print(f"[*] Codewars qidiruv (faqat Python): mavzu='{topic_query}', kyu='{kyu_level}'...")
        
        # Kyu mapping to rank query parameter (-8, -7, etc.)
        rank_param = ""
        if kyu_level:
            m = re.search(r'([1-8])', str(kyu_level))
            if m:
                rank_num = -int(m.group(1))
                rank_param = f"&r%5B%5D={rank_num}"

        # Intelligent query/tags mapping for pure programming topics
        topic_lower = topic_query.lower().replace(' ', '_')
        query_candidates = [f"q={topic_query}"]
        
        TOPIC_MAP = {
            'while_loop': ['q=while', 'tags=Fundamentals', 'q=loop'],
            'for_loop': ['q=loop', 'tags=Fundamentals', 'q=range'],
            'string': ['tags=Strings', 'q=string'],
            'list': ['tags=Arrays', 'q=list', 'q=array'],
            'arithmetic_operators': ['tags=Mathematics', 'tags=Algebra', 'q=math'],
            'if_related_homework': ['tags=Fundamentals', 'tags=Logic', 'q=condition'],
            'logics': ['tags=Logic', 'tags=Fundamentals'],
            'oop': ['tags=Object-oriented%20Programming', 'q=class'],
            'regular_expressions': ['tags=Regular%20Expressions', 'q=regex'],
            'algorithms': ['tags=Algorithms', 'q=sort', 'q=algorithm'],
            'dictionary': ['q=dictionary', 'q=hashmap', 'tags=Fundamentals'],
            'built_in': ['tags=Fundamentals']
        }
        if topic_lower in TOPIC_MAP:
            query_candidates = TOPIC_MAP[topic_lower]

        found_ids = []
        seen = set()

        for q_part in query_candidates:
            for page in range(max_pages):
                url = f"{self.SEARCH_URL}?{q_part}&beta=false{rank_param}&order_by=rank_id%20desc&page={page}"
                try:
                    resp = self.session.get(url, timeout=15)
                    if resp.status_code != 200:
                        break
                    ids = re.findall(r'/kata/([a-f0-9]{24})', resp.text)
                    new_in_page = 0
                    for pid in ids:
                        if pid not in seen:
                            seen.add(pid)
                            found_ids.append(pid)
                            new_in_page += 1
                    if new_in_page == 0:
                        break
                    time.sleep(self.delay)
                except Exception as e:
                    print(f"[!] Qidiruv sahifasini o'qishda xatolik (sahifa {page}): {e}")
                    break

        print(f"[✓] Qidiruv natijasida {len(found_ids)} ta nomzod masala topildi.")
        return found_ids
