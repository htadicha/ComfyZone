# Wireframe – Product Detail

```
┌─────────────────────────────┬──────────────────────────────────────────────┐
│ Image carousel (60%)        │ Product info (40%)                           │
│ • Primary image             │ • Product title + price                      │
│ • Thumbnail rail            │ • Rating summary + review count              │
│                             │ • Short description                          │
│                             │ • Stock status + quantity selector           │
│                             │ • Variation selects (color/size)             │
│                             │ • Add to cart button                         │
├─────────────────────────────┴──────────────────────────────────────────────┤
│ Reviews block                                                               
│ • List top 5 approved reviews                                               
│ • CTA: “Manage your review” (auth only)                                     
│ • Guests see login prompt                                                   
├──────────────────────────────────────────────────────────────────────────────┤
│ Related products (4-up grid)                                                 
│ • Cards mirror home layout                                                   │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Key Decisions

- **Review CTA** links to the unified CRUD page introduced in this sprint, satisfying LO1.9 + LO1.13 evidence.
- **Metadata**: `meta_description` pulls from `product.meta_description` so SEO snippets match catalog copy.
- **Accessibility**: Carousel controls labelled for screen readers; images carry `alt_text`.







