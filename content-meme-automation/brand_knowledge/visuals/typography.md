# Rekt CEO: Typography Guidelines

Our typography must strike a balance between the unpolished, recognizable "shitpost" aesthetic and a legible, authoritative brand voice.

## 1. Web & UI Typography

*(Note: These are standard guidelines extrapolated from the `brand_config.json`; refer to the explicit CSS or frontend frameworks for exact programmatic implementations).*

*   **Headers & Titles:** 
    *   Should employ bold, commanding geometric sans-serif or display fonts (if specifically designated in frontend code) to convey the "CEO" authority.
    *   Must be displayed in **ALL CAPS** when announcing something crucial.

*   **Body Text:**
    *   A clean, modern comic-sans to ensure high legibility for long-form reading (like the manifesto or utility explanations).
    *   High contrast is mandatory (e.g., `#ffffff` text on `#0c0c0c` backgrounds).

## 2. Meme Generation Typography

When generating memes or automated social graphics, we adhere strictly to the classic internet meme aesthetic, but we refine it with our distinct framing.

*   **Font Family:** `Impact`
    *   **Why:** It is the undisputed king of meme fonts. It is instantly recognizable by the "degen" audience and commands immediate attention in a fast-scrolling feed.

*   **Styling Rules:**
    *   **Case:** `UPPERCASE` is highly preferred for visual weight, though sentence case is allowed for longer narrative jokes or "broetry" formatting within the image.
    *   **Weight:** `Bold`.
    *   **Legibility (The Meme Stroke):** Meme text MUST have a thick stroke/outline to ensure it is readable over chaotic backgrounds.
        *   **Fill Color:** Pure White (`#ffffff`)
        *   **Stroke Color:** Void Black (`#000000`)
        *   **Stroke Width:** 2px minimum (scale appropriately to the image resolution).

*   *(Secondary Fallback: If `Impact` is unavailable or the user explicitly dictates an absurdist/ironic tone, `Comic Sans` is technically permissible as per the brand config, but should be used sparingly for maximum ironic effect).*
