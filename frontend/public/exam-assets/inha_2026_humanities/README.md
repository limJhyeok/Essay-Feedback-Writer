# Inha 2026 Humanities — Image Assets

This directory serves graph images for the 2026 Inha humanities mock
essay, Question 2. Images are served as static files by Vite at
`/exam-assets/inha_2026_humanities/<filename>` and referenced from
`backend/app/data/ksat/2026_inha_official_essay/humanities/passages/q_2.md`.

## Required files

Screenshot these from the source PDF
(`backend/app/data/ksat/2026_inha_official_essay/humanities/(인문) 2026학년도 논술 모의고사 문제지.pdf`)
and drop them here with the exact filenames below:

| Filename | Caption (PDF label) | Page |
|---|---|---|
| `q2_fig1.png` | `<그림 1>` A국의 기준금리와 BIS 신용갭 추이 | 7 |
| `q2_fig2.png` | `<그림 2>` A공공보증기관의 연도별 매출 및 당기순이익 | 8 |
| `q2_fig3.png` | `<그림 3>` A 공공 보증기관 전월세보증금 대위변제액 | 8 |
| `q2_fig4.png` | `<그림 4>` 정책유형별 재정승수 비교 | 9 |
| `q2_fig5.png` | `<그림 5>` 각국의 연도별 PISA 수학 평균 점수 | 10 |

## Notes

- Tables (`<표 1>`, `<표 2>`, `<표 3>`) live in the markdown as pipe
  tables — do NOT create image files for them.
- Aspect ratio / cropping is up to the author; the frontend renders
  the image responsively via `<img>` inside `marked.js` output.
- Adding more exams follows the same convention: create a sibling
  directory `<exam_slug>/` with its own README and image files.
