# Codewars Agent System Rules & Guidelines

Ushbu qoidalar Codewars agentining barcha operatsiyalari uchun majburiydir. Agent 2 ta asosiy vazifani bajaradi:
1. **Profil Tahlili:** Foydalanuvchi ishlagan masalalarni yuklab, ularni dasturlash mavzulariga ajratish va Google Sheets'ga yozish.
2. **Yangi Masalalar Qidiruvi (Hunter):** Foydalanuvchi ilgari **ishlamagan** yangi masalalarni so'ralgan mavzu, kyu darajasi va miqdor bo'yicha qidirib topish, **faqat Python** tilida yechiladiganlarini ajratish, shartini chuqur tahlil qilish va Google Sheets'ga yozish.

---

## 1. Qidiruv va Anti-Dublikat Qoidalari

1. **Faqat Python Dasturlash Tili Qat'iy Talabi:**
   - Qidiruv natijasida olinadigan har bir masala **albatta Python tilini qo'llab-quvvatlashi shart** (`'python' in kata_details['languages']`).
   - Python tilida yechimi bo'lmagan (faqat JS, Java, C++ va h.k. bo'lgan) masalalar 100% chiqarib tashlanadi.
   - Jadvaldagi `Lanaguage` ustuniga `Python` deb yoziladi.
2. **Yagona Kalit (Unique Identifier):**
   - Masalalarni solishtirish va dublikatlarni tekshirish faqat **24 xonali Codewars Hex ID** (`kata_id`) orqali amalga oshiriladi.
3. **Qat'iy 0% Dublikat Kafolati:**
   - Yangi masalalar qidirilganda, foydalanuvchi Codewars profilida avval ishlagan birorta ham masala (`id in solved_ids`) yangi tavsiya ro'yxatiga tushmasligi shart.
4. **Yechilish Algoritmi bo'yicha Tahlil (Relevance & Implementation Analysis):**
   - Har bir kataga kiriladi (`GET /api/v1/code-challenges/{id}`).
   - Masalaning sharti (description), teglari (tags) va nomi tahlil qilinadi.
   - Masala Codewars matnidagi tasodifiy so'zlar bilan emas, balki **haqiqatda Python kodida qanday yechilish mohiyati (yechish algoritmi)** bo'yicha tekshiriladi.

---

## 2. Dasturlash Mavzulari Tasnifi (Sof Dasturlash Standartlari)

Masalalar Codewars'dagi mavhum soha nomlari bilan emas (masalan: `geometry` yoki `puzzles` kabi emas), balki **haqiqiy Python dasturlash sintaksisi va tushunchalari** bo'yicha ajratiladi:

1. `while_loop`: Haqiqiy `while` shartli sikli talab etiladigan masalalar (shart bajarilgunicha simulyatsiya, populyatsiya o'sishi, collatz, to'p sakrashi, raqamlarni bittagacha qisqartirish, qadamlar soni).
2. `for_loop`: `for` va `range(...)` orqali oraliq bo'yicha iteratsiyalar, qadamlar, n marta takrorlanishlar, shakl chizish, ko'paytirish jadvali, ketma-ketliklar yig'indisi.
3. `if_related_homework`: Shart operatorlari (`if`, `elif`, `else`, shartli tarmoqlanish, taqqoslash, baholash, o'yin mantiqi).
4. `arithmetic_operators`: Arifmetik amallar, formulalar, hisob-kitoblar (geometrik shakllar yuzi/hajmi, koordinatalar, burchaklar, darajalar, vaqt konvertatsiyasi).
5. `string`: Satrlar va ularning metodlari (`strip`, `split`, `replace`, slicing, palindrom, matn tahlili va formatlash).
6. `list`: Ro'yxatlar va massivlar (`append`, `pop`, indexing, list comprehension, massiv elementlarini qayta ishlash).
7. `dictionary`: Lug'atlar (dict, kalit-qiymat, hashmap, lookup tables, mapping).
8. `built_in`: Ichki va standart kutubxona funksiyalari (`len`, `min`, `max`, `sum`, `abs`, `round`, `type`, `math`...).
9. `oop`: Obyektga yo'naltirilgan dasturlash (Class, `__init__`, metodlar, merosxo'rlik).
10. `regular_expressions`: Regex (`re` moduli) orqali andoza bo'yicha qidirish va matn tahlili.
11. `algorithms`: Algoritmlar, saralash (sorting), rekursiya, ketma-ketliklar, sonlar nazariyasi, ikkilik qidiruv.
12. `logics`: Mantiqiy operatorlar (`and`, `or`, `not`, boolean taqqoslashlar, rostlik jadvallari).
13. `fundamentals_umumiy`: Faqat va faqat yuqoridagi sof mavzularning hech biriga tushmagan o'ta sodda umumiy sintaksis (bunday holat minimal bo'lishi shart).

---

## 3. Qiyinlik Darajasi (Difficulty)

- **`Basic`**: `8 kyu` va `7 kyu` masalalari.
- **`Advanced`**: `6 kyu`, `5 kyu`, `4 kyu`, `3 kyu`, `2 kyu`, `1 kyu` masalalari.

---

## 4. Google Sheets Formatlash Standartlari (2-rasm andozasi)

Google Sheet'ga yoziladigan har bir mavzu jadvali quyidagi formatda bo'lishi shart:
1. **Ustunlar tartibi:**
   - `# Column 1` (Tartib raqami: 1, 2, 3...)
   - `Problem name` (Bosiladigan havola: `=HYPERLINK("<url>", "<name> | Codewars")`)
   - `Problem id` (24 xonali Codewars ID)
   - `topic` (Mavzu nomi)
   - `Difficulty` (`Basic` yoki `Advanced`)
   - `Lanaguage` (`Python`)
2. **Sarlavha qatori (Header):**
   - Fon rangi: To'q yashil (`#0D6133` / RGB: 13, 97, 51)
   - Matn: Oq rang, qalin (bold), 10pt
   - Qotirilgan (Freeze 1 row) bo'lishi shart.

---

## 5. Avtorizatsiya

- Google Sheets xizmati bilan ishlashda doimo loyihadagi `/home/sanjar/Desktop/lessons/credentials.json` service account fayli ishlatiladi.
- Bot pochtasi: `sheet-bot@light-rhythm-504607-j1.iam.gserviceaccount.com`.

---

## 6. Loyiha Google Sheet Havolalari

- **Tugatilgan (Ishlangan) Masalalar Jadvali:**
  `https://docs.google.com/spreadsheets/d/17_vwGPdOGXwsiukClGIV4snpjOw-vRu4Ob67VPY2GrM/edit?usp=sharing`
  (ID: `17_vwGPdOGXwsiukClGIV4snpjOw-vRu4Ob67VPY2GrM`)
- **Yangi Qidirilgan (So'ralgan Mavzular) Masalalar Jadvali:**
  `https://docs.google.com/spreadsheets/d/1VWc8OrNu-d-aj33zMq0hSBR7r5lf0jczVmQdHGnCZPs/edit?usp=sharing`
  (ID: `1VWc8OrNu-d-aj33zMq0hSBR7r5lf0jczVmQdHGnCZPs`)
- **Qo'shilmagan Masalalar (Diff) Jadvali:**
  `https://docs.google.com/spreadsheets/d/1DwIWV45q2bvraAnd1EIw-BmJzfJfLOGSgdrhhIDE3KE/edit?usp=sharing`
  (ID: `1DwIWV45q2bvraAnd1EIw-BmJzfJfLOGSgdrhhIDE3KE`)
