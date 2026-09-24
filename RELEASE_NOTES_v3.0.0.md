# 🎮 SkinRate Calculator Pro v3.0.0 Release Notes

Welcome to the major **v3.0.0 Overhaul** of **SkinRate Calculator Pro**! This release brings a completely revamped, ultra-modern desktop UI, blazing fast startup optimizations, verified mathematical fee engines, highly requested CS2 trader features, and full GitHub release automation.

---

## 🌟 What's New in v3.0.0

### 🚀 1. Modern Desktop UI with Top Application Toolbar
- **Native Top Application Toolbar**: Streamlined top navigation bar with CS2-styled brand logo, quick tab mode switcher, theme toggle, calculation history, trade slip exporter, settings, and reset button.
- **Dark & Light Modes**: Implemented high-contrast CS2 Slate Dark Theme (default) and clean Light Theme with 1-click instant switching (`Ctrl+T`).
- **High-DPI Razor-Sharp Antialiasing**: Added native Windows DPI scaling integration (`shcore.SetProcessDpiAwareness`), rendering razor-sharp fonts and borders across 1080p, 2K, and 4K displays.
- **Preset Quick-Chips**: One-click preset chips for Amount (`+$10`, `+$25`, `+$50`, `+$100`, `$200`), Item Rate (`118`, `120`, `121`, `122`, `125`), and Wallet Rate (`114`, `116`, `118`, `120`).
- **Visual Feedback**: Buttons morph to `✓ Copied` with smooth animations and toast notifications.

---

### 🧮 2. Precise Steam Market Fee Calculation & Flip Profit
- **Exact Steam 15% Community Market Fee Engine**: Fixed previous tax estimation bugs. Now uses Valve's exact integer cent algorithm (Valve 5% min $0.01 + CS2 Game 10% min $0.01).
- **Dual Perspective Analysis**:
  - *If you want to receive $X* ➔ Calculates the exact price buyer must pay on Steam Market.
  - *If buyer pays $X* ➔ Calculates the exact amount deposited into your Steam Wallet.
- **CS2 Skin Flipping & ROI Calculator**: Calculate trade profit when buying from external markets (Buff, CSFloat) and selling on Steam Market, factoring in Steam fees, net wallet received, cashout rate, net BDT profit, and Return on Investment (ROI %).

---

### 💳 3. Comprehensive Mobile Financial Services (MFS) Cashout
- **Customized for Bangladeshi CS2 Traders**:
  - **bKash Agent Cashout** (1.85% / 18.5 Tk per 1,000 Tk)
  - **bKash Priyo Number / App** (1.49% / 14.9 Tk per 1,000 Tk)
  - **Nagad App** (1.25% / 12.5 Tk per 1,000 Tk)
- **Dual Perspectives**:
  - **Buyer Sends (Fee Added)**: How much the buyer must send via MFS so the seller receives the exact agreed amount after cashing out.
  - **Cash in Hand (Fee Deducted)**: How much liquid cash the seller receives after agent withdrawal if buyer sends the base cost.

---

### ⇄ 4. Reverse Calculator (BDT Budget ➔ USD Skins / Wallet)
- Answer customer questions like: *"I have ৳5,000, how much knife or skin can I get?"*
- Calculates exact USD skin value, USD wallet balance, and required Steam Market listing price.
- Supports MFS fee deductions (Agent 1.85%, Priyo 1.49%, Nagad 1.25%).

---

### 📊 5. Live Cheat Sheet Rate Matrix ($1 to $1,000)
- Interactive cheat sheet table displaying calculations for:
  `$1, $2.50, $5, $10, $15, $20, $25, $50, $75, $100, $150, $200, $250, $500, $1,000`
- Updates immediately when Item Rate or Wallet Rate is adjusted.
- **1-Click Copy Table**: Formatted ASCII table ready to share with clients and trade groups.

---

### 📋 6. One-Click Formatted Trade Slip Exporter
- Copy a clean trade slip formatted specifically for Facebook CS2 groups, Discord, Messenger, or WhatsApp.
- Multiple styles available: **Box Unicode Borders**, **Discord Markdown**, and **Compact SMS**.

---

### ⚙️ 7. Persistent Settings & Trade History
- Automatically remembers your default Item Rate, Wallet Rate, custom cashout fee, and theme between sessions.
- Configurable **BDT Comma Formatting** (disabled by default as `৳12000` per Bangladeshi trader preferences; can be enabled as `৳12,000` in Settings).
- Built-in **Calculation History** (saves last 30 quotes with 1-click restore).

---

### ⚡ 8. Launch Speed & Packaging Optimizations
- **Instant Launch**: Sub-second startup (<0.1s in portable mode) utilizing lightweight native Tkinter without bloated external GUI frameworks.
- **Cleaned PyInstaller Build**: Excluded unused standard libraries (SQLite, multiprocessing, urllib, unittest, pydoc, etc.), reducing standalone binary size.
- **Two Distribution Formats**:
  1. `SkinRate-Calculator-v3.0.0-Windows.exe`: Standalone portable single `.exe` file.
  2. `SkinRate-Calculator-v3.0.0-Portable.zip`: Zero-temp-extraction directory version for instant 0.05s startup.

---

## ⌨️ Keyboard Shortcuts Reference

| Shortcut | Action |
| :--- | :--- |
| **`Enter`** | Calculate Active View |
| **`Esc`** | Clear Fields / Reset Defaults |
| **`Ctrl + C`** | Open Trade Slip Exporter |
| **`Ctrl + T`** | Toggle Dark / Light Theme |
| **`Ctrl + H`** | View Calculation History |
| **`Ctrl + S`** | Open Settings & Preferences |
| **`Ctrl + 1`** | Switch to Standard Calculator |
| **`Ctrl + 2`** | Switch to Reverse Calculator |
| **`Ctrl + 3`** | Switch to Steam Market & Profit |
| **`Ctrl + 4`** | Switch to Rate Cheat Sheet |

---

## 📦 Downloads & Verification

Download the release assets below:
- **`SkinRate-Calculator-v3.0.0-Windows.exe`** (Single-file portable executable)
- **`SkinRate-Calculator-v3.0.0-Portable.zip`** (Fast-launch folder version)
- **`checksums.txt`** (SHA-256 verification hashes)

Enjoy trading! 🎯
