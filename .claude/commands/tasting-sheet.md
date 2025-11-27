---
description: Generate wine tasting sheet from product names
---

You are tasked with generating a wine tasting sheet based on the following natural language request:

**User request:** {{input}}

## Instructions:

1. **Download the product data:**
   - Run `python test_sheet.py` to download the latest product_data.xlsx from Google Drive
   - Load the data to understand available producers and cuvees

2. **Parse the natural language request:**
   - Understand modifiers:
     - "both X" / "all X" = all products from producer X or all products with X in the name
     - "X and Y" = separate items X and Y
     - Numbers like "2 X" = find 2 products matching X
   - Ignore filler words: "the", "from", "by", etc.
   - Extract meaningful product identifiers from the remaining text

3. **Match each identifier:**
   - Try matching against PRODUCER first (case-insensitive, partial match)
   - If no producer match, try matching against CUVEE_NAME
   - If match is a producer + "both"/"all" modifier, select ALL rows for that producer
   - If match is ambiguous (multiple possible matches), continue to step 4

4. **Handle ambiguity:**
   - If an identifier matches exactly ONE product row → add it automatically
   - If an identifier matches MULTIPLE rows → use AskUserQuestion to show matches and let the user pick which one(s)
   - If an identifier matches ZERO rows → warn the user and skip it

5. **Generate the document:**
   - Modify `generate_tasting_sheet.py` to accept a list of specific row indices instead of using the "Chosen" column
   - Run the modified script to generate the tasting sheet with only the matched products
   - Show the user which products were included in the final document

**Examples:**
- "both scopa and both realce" → all products from Scopa producer + all products from Realce producer
- "da mar prosecco, scopa rosso" → Da Mar's prosecco + Scopa's rosso cuvee
- "all the bottes rouges" → all products from Bottes Rouges producer
- "leon, tempranillo" → Leon cuvee + any cuvee with tempranillo in the name

**Important:** Be extremely flexible. The user is being conversational and lazy. Your job is to intelligently interpret what they mean by analyzing the actual data in the sheet.
