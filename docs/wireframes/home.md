# Wireframe – Home / Landing

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Hero: headline + CTA                                                         │
│ ┌─────────────┐ ┌──────────────────────────────────────────────────────────┐ │
│ │ Value copy  │ │ Lifestyle image                                         │ │
│ │ • H1        │ │ • Lazy-loaded to keep LCP < 2.5s                        │ │
│ │ • Paragraph │ │                                                          │ │
│ │ • CTA pair  │ │                                                          │ │
│ └─────────────┘ └──────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────┤
│ Featured products (3-up cards)                                               │
│ [Card]  [Card]  [Card]                                                       │
│ • Image w/ alt text                                                          │
│ • Title                                                                      │
│ • Price                                                                      │
│ • Quick action icon                                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│ Why Choose Us                                                                │
│ • 4 feature tiles (Shipping, Shopping ease, Support, Returns)                │
├──────────────────────────────────────────────────────────────────────────────┤
│ Newsletter CTA (footer hero)                                                 │
│ • Email + name inputs                                                        │
│ • Clear consent copy                                                         │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Notes

- Navigation exposes Shop/About/Services/Contact plus account/cart icons.
- Hero CTA buttons route to `shop/` and `about/`.
- Featured products link to `/product/<slug>/`.
- Newsletter form posts to `marketing:subscribe` and feeds Merit LO5 evidence.



