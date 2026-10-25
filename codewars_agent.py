#!/usr/bin/env python3
"""
Codewars Agent
==============
Foydalanuvchi Codewars profilini tahlil qiluvchi, mavzular bo'yicha saralovchi
va so'rov bo'yicha yangi (ishlanmagan) masalalarni topib Google Sheet'ga
avtomatik saqlovchi professional agent.
"""

import sys
import os
import argparse
import json

# Add tools directory to path
tools_dir = os.path.join(os.path.dirname(__file__), '.agents', 'skills', 'codewars-agent', 'tools')
if tools_dir not in sys.path:
    sys.path.insert(0, tools_dir)

from codewars_client import CodewarsClient
from topic_classifier import TopicClassifier
from sheets_client import SheetsClient

DEFAULT_CREDENTIALS = os.path.join(os.path.dirname(__file__), 'credentials.json')
DEFAULT_COMPLETED_SHEET = '17_vwGPdOGXwsiukClGIV4snpjOw-vRu4Ob67VPY2GrM'
DEFAULT_NEW_KATAS_SHEET = '1VWc8OrNu-d-aj33zMq0hSBR7r5lf0jczVmQdHGnCZPs'

class CodewarsAgent:
    def __init__(self, credentials_path=DEFAULT_CREDENTIALS):
        self.cw = CodewarsClient()
        self.classifier = TopicClassifier()
        self.sheets = SheetsClient(credentials_path)

    def analyze_profile(self, username, target_sheet_id=DEFAULT_COMPLETED_SHEET):
        """1-VAZIFA: Profilni to'liq tahlil qilish va mavzular bo'yicha saralab Sheet'ga yozish."""
        print(f"\n==========================================")
        print(f"📊 PROFIL TAHLILI: @{username}")
        print(f"==========================================\n")

        # 1. Barcha ishlangan masalalarni tortish
        completed = self.cw.get_user_completed_katas(username)
        if not completed:
            print(f"[X] Masalalar topilmadi yoki profil bo'sh.")
            return []

        # 2. Mavzular bo'yicha parallel tahlil qilish
        print(f"\n[*] {len(completed)} ta masalaning shartlari va teglari Codewars API orqali parallel o'qilmoqda...")
        all_ids = [it['id'] for it in completed]
        details_map = self.cw.get_katas_details_bulk(all_ids, max_workers=10)

        topic_groups = {}
        for it in completed:
            pid = it['id']
            det = details_map.get(pid)
            if det:
                name = det['name']
                tags = det['tags']
                desc = det['description']
                rank = det['rank']
                url = det['url']
            else:
                name = it['name']
                tags = []
                desc = ""
                rank = "8 kyu"
                url = f"https://www.codewars.com/kata/{pid}"

            topic = self.classifier.classify(name=name, tags=tags, description=desc)
            diff = self.classifier.get_difficulty(rank)

            topic_groups.setdefault(topic, []).append({
                'id': pid,
                'name': name,
                'url': url,
                'topic': topic,
                'difficulty': diff,
                'language': 'Python/C++'
            })

        print(f"\n[✓] Tahlil yakunlandi! Jami {len(completed)} ta masala quyidagi mavzularga ajratildi:")
        for t, items in sorted(topic_groups.items(), key=lambda x: -len(x[1])):
            print(f"   • {t}: {len(items)} ta")

        # 3. Google Sheet'ga to'liq formatda yozish (1-rasm va 2-rasm andozasi)
        if target_sheet_id:
            print(f"\n[*] Google Sheet ({target_sheet_id}) ga to'liq mavzular bo'yicha yozilmoqda...")
            self.sheets.sync_full_topics_spreadsheet(target_sheet_id, topic_groups)

        return topic_groups

    def hunt_new_katas(self, username, topic, kyu, count=10, target_sheet_id=DEFAULT_NEW_KATAS_SHEET):
        """2-VAZIFA: Foydalanuvchi ISHLAMAGAN yangi masalalarni topish va tahlil qilib saqlash."""
        print(f"\n==========================================")
        print(f"🎯 YANGI MASALALAR QIDIRUVI (HUNTER)")
        print(f"==========================================")
        print(f"Foydalanuvchi: @{username}")
        print(f"Qidirilayotgan Mavzu: '{topic}'")
        print(f"Talab qilingan Daraja: '{kyu}'")
        print(f"Kerakli Miqdor: {count} ta masala\n")

        # 1. Foydalanuvchi ilgari ishlagan barcha masalalar bazasini olish (Dublikat bo'lmasligi uchun)
        print(f"[*] @{username} ilgari ishlagan masalalari tekshirilmoqda...")
        solved_katas = self.cw.get_user_completed_katas(username)
        solved_ids = {k['id'] for k in solved_katas}
        print(f"[✓] {len(solved_ids)} ta avval ishlangan masala ID lari ro'yxatga olindi (ular chiqarib tashlanadi).\n")

        # 2. Codewars'dan qidirish
        candidate_ids = self.cw.search_katas(topic_query=topic, kyu_level=kyu, max_pages=6)
        
        found_matches = []
        checked_count = 0

        print(f"\n[*] Masalalar chuqur tahlil qilinmoqda (sharti, teglari va kyu darajasi)...")
        for pid in candidate_ids:
            if len(found_matches) >= count:
                break

            checked_count += 1
            # 100% Anti-dublikat tekshiruvi: Agar foydalanuvchi bu masalani allaqachon ishlagan bo'lsa, o'tkazib yuboriladi!
            if pid in solved_ids:
                continue

            # Kataga kirib uni tahlil qilish
            details = self.cw.get_kata_details(pid)
            if not details:
                continue

            # QAT'IY QOIDA: Faqat Python tilida yechilishi mumkin bo'lgan masalalarni tanlash
            supported_langs = [str(l).lower() for l in details.get('languages', [])]
            if 'python' not in supported_langs:
                continue

            # Darajani tekshirish
            kata_rank = details.get('rank', '').lower()
            if kyu and str(kyu).lower() not in kata_rank:
                # If specific kyu requested, ensure it matches
                continue

            # Shart va mavzu mosligini tahlil qilish
            is_match = self.classifier.matches_target(
                target_topic=topic,
                name=details.get('name', ''),
                tags=details.get('tags', []),
                description=details.get('description', '')
            )

            if is_match:
                diff = self.classifier.get_difficulty(details.get('rank', ''))
                found_matches.append({
                    'id': details['id'],
                    'name': details['name'],
                    'url': details['url'],
                    'topic': topic.replace(' ', '_'),
                    'difficulty': diff,
                    'language': 'Python'
                })
                print(f"   [+] Topildi ({len(found_matches)}/{count}): {details['name']} ({details.get('rank')})")

        print(f"\n[✓] Jami {checked_count} ta masala tekshirildi, {len(found_matches)} ta mos yangi Python masalasi topildi!")

        # 3. Google Sheet'ga yozish
        if found_matches and target_sheet_id:
            tab_name = topic.lower().replace(' ', '_')
            self.sheets.write_katas_to_topic_sheet(
                spreadsheet_id=target_sheet_id,
                topic_name=tab_name,
                katas=found_matches,
                clear_existing=False
            )
            print(f"[✓] Masalalar Google Sheet'ning '{tab_name}' sahifasiga muvaffaqiyatli saqlandi!")

        return found_matches

def main():
    parser = argparse.ArgumentParser(description="Codewars Multi-Task Agent")
    subparsers = parser.add_subparsers(dest="command", help="Agent buyrug'i")

    # Command 1: analyze
    p_analyze = subparsers.add_parser("analyze", help="Profilni tahlil qilish va mavzularga ajratish")
    p_analyze.add_argument("--user", required=True, help="Codewars username")
    p_analyze.add_argument("--sheet", default=DEFAULT_COMPLETED_SHEET, help="Google Sheet ID")

    # Command 2: hunt
    p_hunt = subparsers.add_parser("hunt", help="Yangi (ishlanmagan) masalalarni qidirish va saqlash")
    p_hunt.add_argument("--user", required=True, help="Codewars username (ishlanganlarni o'tkazib yuborish uchun)")
    p_hunt.add_argument("--topic", required=True, help="Qidirilayotgan mavzu (masalan: for_loop, string, algorithms)")
    p_hunt.add_argument("--kyu", required=True, help="Talab qilinadigan daraja (masalan: '8 kyu', '7 kyu')")
    p_hunt.add_argument("--count", type=int, default=10, help="Kerakli masalalar soni (masalan: 10)")
    p_hunt.add_argument("--sheet", default=DEFAULT_NEW_KATAS_SHEET, help="Google Sheet ID")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    agent = CodewarsAgent()

    if args.command == "analyze":
        agent.analyze_profile(username=args.user, target_sheet_id=args.sheet)
    elif args.command == "hunt":
        agent.hunt_new_katas(
            username=args.user,
            topic=args.topic,
            kyu=args.kyu,
            count=args.count,
            target_sheet_id=args.sheet
        )

if __name__ == '__main__':
    main()
