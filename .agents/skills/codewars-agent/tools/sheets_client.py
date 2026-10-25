import gspread

class SheetsClient:
    """Google Sheets bilan professional formatlash (1-rasm va 2-rasm andozasi) asosida ishlovchi mijoz."""

    GREEN_HEADER_BG = {"red": 0.05, "green": 0.38, "blue": 0.20} # #0D6133
    WHITE_TEXT = {"red": 1.0, "green": 1.0, "blue": 1.0}

    def __init__(self, credentials_path="credentials.json"):
        self.gc = gspread.service_account(filename=credentials_path)

    def write_katas_to_topic_sheet(self, spreadsheet_id, topic_name, katas, clear_existing=False):
        """Topilgan masalalarni Google Sheet'dagi tegishli mavzu sahifasiga 2-rasm formatida yozadi."""
        print(f"[*] Google Sheet'ga yozilmoqda ({spreadsheet_id} -> varaq: '{topic_name}')...")
        sh = self.gc.open_by_key(spreadsheet_id)

        # Get or create worksheet
        worksheets = {ws.title: ws for ws in sh.worksheets()}
        if topic_name in worksheets:
            ws = worksheets[topic_name]
        else:
            ws = sh.add_worksheet(title=topic_name, rows=len(katas) + 20, cols=6)

        header = ['# Column 1', 'Problem name', 'Problem id', 'topic', 'Difficulty', 'Lanaguage']
        
        # Check existing rows if appending
        existing_rows = ws.get_all_values()
        has_valid_header = existing_rows and any(existing_rows[0]) and str(existing_rows[0][0]).strip().startswith('#')
        
        rows_to_write = []
        if not has_valid_header or clear_existing:
            rows_to_write.append(header)
            existing_ids = set()
            start_idx = 1
            ws.clear()
        else:
            start_idx = len(existing_rows)
            existing_ids = {r[2].strip() for r in existing_rows[1:] if len(r) > 2}

        added_count = 0
        for it in katas:
            pid = it['id']
            if pid in existing_ids:
                continue
            existing_ids.add(pid)
            clean_name = it['name'].replace('"', '""')
            display_title = f"{clean_name} | Codewars"
            link_formula = f'=HYPERLINK("{it["url"]}", "{display_title}")'
            
            curr_num = start_idx + added_count
            rows_to_write.append([
                curr_num,
                link_formula,
                pid,
                it.get('topic', topic_name).replace('_', ' '),
                it.get('difficulty', 'Basic'),
                it.get('language', 'Python')
            ])
            added_count += 1

        if not has_valid_header or clear_existing:
            if rows_to_write:
                ws.update(values=rows_to_write, range_name=f"A1:F{len(rows_to_write)}", value_input_option='USER_ENTERED')
        else:
            if rows_to_write:
                next_row = len(existing_rows) + 1
                end_row = next_row + len(rows_to_write) - 1
                ws.update(values=rows_to_write, range_name=f"A{next_row}:F{end_row}", value_input_option='USER_ENTERED')

        # Apply 2-rasm green styling and freeze header
        self.apply_green_header_style(sh, ws.id)
        print(f"[✓] {added_count} ta masala muvaffaqiyatli saqlandi!")
        return added_count

    def apply_green_header_style(self, sh, sheet_id):
        """2-rasmdagi yashil sarlavha va qotirilgan 1-qator dizaynini beradi."""
        requests = [
            {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": 6
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": self.GREEN_HEADER_BG,
                            "textFormat": {
                                "bold": True,
                                "foregroundColor": self.WHITE_TEXT,
                                "fontSize": 10
                            },
                            "horizontalAlignment": "LEFT"
                        }
                    },
                    "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
                }
            },
            {
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": sheet_id,
                        "gridProperties": {"frozenRowCount": 1}
                    },
                    "fields": "gridProperties.frozenRowCount"
                }
            }
        ]
        try:
            sh.batch_update({"requests": requests})
        except Exception as e:
            print(f"[!] Dizayn qo'llashda ogohlantirish: {e}")

    def sync_full_topics_spreadsheet(self, spreadsheet_id, topic_groups):
        """Barcha mavzularni to'liq 1-rasm (TOPIC) va 2-rasm (mavzular) andozasida yaratadi/yangilaydi."""
        print(f"[*] Google Sheet ({spreadsheet_id}) to'liq mavzular bo'yicha shakllantirilmoqda...")
        sh = self.gc.open_by_key(spreadsheet_id)

        sorted_topics = sorted(topic_groups.keys(), key=lambda t: -len(topic_groups[t]))
        existing = {ws.title: ws for ws in sh.worksheets()}

        # 1. Main TOPIC sheet
        if 'TOPIC' in existing:
            ws_main = existing['TOPIC']
        else:
            ws_main = sh.add_worksheet(title='TOPIC', rows=len(sorted_topics) + 15, cols=4, index=0)
            existing['TOPIC'] = ws_main

        # 2. Topic worksheets
        topic_refs = {}
        for t in sorted_topics:
            items = topic_groups[t]
            if t in existing:
                ws = existing[t]
            else:
                ws = sh.add_worksheet(title=t, rows=len(items) + 20, cols=6)
                existing[t] = ws
            topic_refs[t] = ws

        # Delete obsolete worksheets that are not in sorted_topics and not TOPIC
        for old_title, old_ws in list(existing.items()):
            if old_title != 'TOPIC' and old_title not in sorted_topics:
                try:
                    sh.del_worksheet(old_ws)
                    del existing[old_title]
                except Exception as e:
                    print(f"[!] Varaqni o'chirishda ogohlantirish ({old_title}): {e}")

        # Delete default empty Sheet1 if exists
        if 'Sheet1' in existing and len(existing) > 1:
            try:
                sh.del_worksheet(existing['Sheet1'])
            except Exception:
                pass

        # 3. Populate each topic sheet (2-rasm andozasi)
        header_topic = ['# Column 1', 'Problem name', 'Problem id', 'topic', 'Difficulty', 'Lanaguage']
        for t in sorted_topics:
            items = topic_groups[t]
            ws = topic_refs[t]
            rows = [header_topic]
            for idx, it in enumerate(items, start=1):
                clean_name = it['name'].replace('"', '""')
                title_text = f"{clean_name} | Codewars"
                link_formula = f'=HYPERLINK("{it["url"]}", "{title_text}")'
                rows.append([
                    idx,
                    link_formula,
                    it['id'],
                    it.get('topic', t).replace('_', ' '),
                    it.get('difficulty', 'Basic'),
                    it.get('language', 'Python/C++')
                ])
            ws.clear()
            ws.update(values=rows, range_name=f"A1:F{len(rows)}", value_input_option='USER_ENTERED')

        # 4. Populate TOPIC sheet (1-rasm andozasi)
        main_rows = [['TOPIC', 'COUNT', 'NEW', 'TOTAL']]
        total_count = 0
        for t in sorted_topics:
            c = len(topic_groups[t])
            total_count += c
            gid = topic_refs[t].id
            main_rows.append([f'=HYPERLINK("#gid={gid}", "{t}")', c, '', ''])
        main_rows.append(['', '', '', ''])
        main_rows.append(['Overall', total_count, '', ''])

        ws_main.clear()
        ws_main.update(values=main_rows, range_name=f"A1:D{len(main_rows)}", value_input_option='USER_ENTERED')

        # 5. Styling
        requests = [
            # Main sheet bold headers
            {
                "repeatCell": {
                    "range": {
                        "sheetId": ws_main.id,
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": 4
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {"bold": True, "fontSize": 11},
                            "horizontalAlignment": "LEFT"
                        }
                    },
                    "fields": "userEnteredFormat(textFormat,horizontalAlignment)"
                }
            },
            # Overall row bold
            {
                "repeatCell": {
                    "range": {
                        "sheetId": ws_main.id,
                        "startRowIndex": len(main_rows) - 1,
                        "endRowIndex": len(main_rows),
                        "startColumnIndex": 0,
                        "endColumnIndex": 2
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "textFormat": {"bold": True, "fontSize": 11}
                        }
                    },
                    "fields": "userEnteredFormat(textFormat)"
                }
            }
        ]

        # Topic sheets green header styling
        for t in sorted_topics:
            ws = topic_refs[t]
            requests.append({
                "repeatCell": {
                    "range": {
                        "sheetId": ws.id,
                        "startRowIndex": 0,
                        "endRowIndex": 1,
                        "startColumnIndex": 0,
                        "endColumnIndex": 6
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "backgroundColor": self.GREEN_HEADER_BG,
                            "textFormat": {
                                "bold": True,
                                "foregroundColor": self.WHITE_TEXT,
                                "fontSize": 10
                            },
                            "horizontalAlignment": "LEFT"
                        }
                    },
                    "fields": "userEnteredFormat(backgroundColor,textFormat,horizontalAlignment)"
                }
            })
            requests.append({
                "updateSheetProperties": {
                    "properties": {
                        "sheetId": ws.id,
                        "gridProperties": {"frozenRowCount": 1}
                    },
                    "fields": "gridProperties.frozenRowCount"
                }
            })

        sh.batch_update({"requests": requests})
        print(f"[✓] Google Sheet ({spreadsheet_id}) muvaffaqiyatli saqlandi va bezatildi!")
