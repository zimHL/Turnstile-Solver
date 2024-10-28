<div align="center">
 
  <h2 align="center">Cloudflare - Turnstile Solver</h2>
  <p align="center">
A Python-based solution for solving Cloudflare Turnstile challenges quickly (4-6 seconds solve time). The script uses undetected Playwright library to interact with web pages and solve the challenges without running additional browser instances.
    <br />
    <br />
    <a href="https://discord.cyberious.xyz">💬 Discord</a>
    ·
    <a href="https://github.com/sexfrance/sexfrance/Turnstile-Solver">📜 ChangeLog</a>
    ·
    <a href="https://github.com/sexfrance/sexfrance/Turnstile-Solver">⚠️ Report Bug</a>
    ·
    <a href="https://github.com/sexfrance/sexfrance/Turnstile-Solver">💡 Request Feature</a>
  </p>
</div>

### ⚙️ Installation

- Requires: `Python 3.8+`
- Make a python virtual environment: `python3 -m venv venv`
- Source the environment: `venv\Scripts\activate` (Windows) / `source venv/bin/activate` (macOS, Linux)
- Install the requirements: `pip install -r requirements.txt`
- Start: `python3 main.py`

---

### 🔥 Features
- Nice Embeds
- Easy rebrand
- Creates vouch messages
- Can dm the user with his product (file/text) or stock (saved under stock/productname.txt)
- Checks if the user vouched in the rigt format (+rep <@ownerid> quantity product price)
- Checks if the user made a 5 star website review before opening a ticket
- Smart Ticket system included (.replace will close the ticket)
- Auto Scrapes warranty duration from product titles and saves data in product.json (Product id, title and warranty duration)
- Customizable, if you manually changed a warranty duration in json it will not update it while scrapping
- Can add excluded product ids for the warranty scrapper in excluded.json
- Everything in config.json is customizable and changable using the .set command
- Transcribe the replace ticket!
- And more!
---
#### 📹 Preview

![Preview](https://i.imgur.com/YI6RZ5P.gif)

---
### ❗ Disclaimers

- I am not responsible for anything that may happen, such as API Blocking, IP ban, etc.
- This was a quick project that was made for fun and personal use if you want to see further updates, star the repo & create an "issue" [here](https://github.com/sexfrance/Turnstile-Solver/issues/)

---

### 📜 ChangeLog

```diff
v0.0.1 ⋮ 21/10/2024
! Initial release

v0.0.2 ⋮ 10/28/2024
! Modified the script, page.html is now in the scripts, made it faster and less resource intensive, modified the sync logic and made an async version, implemented logmagix logging
```

---

<p align="center">
  <img src="https://img.shields.io/github/license/sexfrance/Turnstile-Solver.svg?style=for-the-badge&labelColor=black&color=f429ff&logo=IOTA"/>
  <img src="https://img.shields.io/github/stars/sexfrance/Turnstile-Solver.svg?style=for-the-badge&labelColor=black&color=f429ff&logo=IOTA"/>
  <img src="https://img.shields.io/github/languages/top/sexfrance/Turnstile-Solver.svg?style=for-the-badge&labelColor=black&color=f429ff&logo=python"/>
</p>


Inspired by [Turnaround](https://github.com/Body-Alhoha/turnaround)
