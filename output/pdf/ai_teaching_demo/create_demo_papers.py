"""Build three related, selectable-text PDFs for a PaperReader demonstration."""

from __future__ import annotations

import json
import re
from pathlib import Path
from xml.sax.saxutils import escape

from pypdf import PdfReader
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
QA = ROOT / "tmp" / "pdfs" / "ai_teaching_demo"
FONT_DIR = ROOT / "public" / "pdfjs" / "standard_fonts"
W, H = A4
LEFT, RIGHT = 68, 51
WIDTH = W - LEFT - RIGHT
INK = colors.HexColor("#24333E")
MUTED = colors.HexColor("#667480")
RULE = colors.HexColor("#DBE2E7")


PAPERS = [
    {
        "id": "A",
        "number": 1,
        "file": "01_AI_as_a_Learning_Partner.pdf",
        "title": ["AI as a Learning Partner"],
        "subtitle": "Bringing AI into Teaching",
        "short": "AI as a Learning Partner",
        "accent": "#176D69",
        "tint": "#EEF7F5",
        "focus": "OPPORTUNITY",
        "abstract": (
            "AI can help teachers explain ideas and help students practice. "
            "However, a useful lesson needs more than a new tool. It needs a clear "
            "learning goal, active student thinking, and a way to check understanding. "
            "This article describes a simple classroom routine: Think, Ask, Check, "
            "and Explain. It also introduces questions about dependence and learning "
            "that the next two articles explore."
        ),
        "pages": [
            {
                "heading": None,
                "sections": [
                    ("1. Start with a learning goal", [
                        ("A01", "AI should support student thinking, not replace it. A teacher should first decide what students need to learn. The goal may be to explain a science idea, compare two reasons, or solve a problem. The teacher can then choose where AI may help. Starting with the tool can lead to a busy lesson in which students produce more work but understand very little."),
                        ("A02", "AI can offer a shorter explanation, a familiar example, or a practice question. A student who is afraid to ask in class may feel more comfortable asking a tool. These uses may open a door to learning. Still, an easy explanation is only a starting point. Students need time to connect it with their own ideas and with the lesson."),
                    ]),
                    ("2. A shared classroom example", [
                        ("A03", "Consider a fictional science class taught by Ms. Lee. Her students are learning how a simple water filter works. The learning goal is to explain what sand and gravel can remove and what they may leave behind. Maya, one student, asks AI for a simple explanation. Ms. Lee asks her to compare the answer with the class reading and a classroom test."),
                        ("A04", "The class uses water with visible dirt for the test. The filtered water may look clearer, but this does not show that it is safe to drink. The students do not taste it. This difference between looking clean and being safe gives the class a reason to question a smooth AI answer. The tool supplies language, while the class supplies evidence."),
                    ]),
                ],
            },
            {
                "heading": "A routine that keeps students thinking",
                "sections": [
                    ("3. Think and ask", [
                        ("A05", "Students should first make an attempt without AI. Maya writes a prediction about the filter and gives a reason. Her first idea does not need to be correct. It gives her something to compare with later advice. This short step also helps Ms. Lee see what Maya already knows. AI can then respond to a real question instead of doing the whole task."),
                        ("A06", "The next step is to ask for limited help. Maya can write, 'Give me one hint about why the water is still unsafe. Do not write my final answer.' She can also ask for an example or a question to test her idea. The teacher models these requests. A clear limit helps students use AI as a helper during thinking, rather than as a source to copy."),
                    ]),
                    ("4. Check and explain", [
                        ("A07", "Students should check an AI claim against evidence they can name. In this lesson, that evidence includes the class reading and what the filter test can actually show. AI may leave out an important limit or give a wrong reason. When students find a problem, they should describe it and correct it. Accepting an answer because it sounds confident is not a careful check."),
                        ("A08", "Students should explain an idea in their own words. Maya closes the AI window and describes why clear water may still be unsafe. She draws a simple filter and labels what each part does. If she cannot explain a step, she returns to that idea for more practice. Rewriting an AI answer with different words is not enough when she still cannot explain the reason."),
                        ("A09", "The four steps form a learning routine: Think, Ask, Check, and Explain. Teachers can use the same routine in other subjects. In a writing lesson, a student might draft a reason, ask for feedback, check whether the feedback fits the task, and explain a revision. The amount of AI help can change, but the student still needs to make and explain important choices."),
                    ]),
                ],
                "callout": ("THE SHARED ROUTINE", "Think > Ask > Check > Explain", "Keep a visible student action at every step."),
            },
            {
                "heading": "The teacher still guides the learning",
                "sections": [
                    ("5. Plan support for different students", [
                        ("A10", "Teachers should explain when AI is allowed and what students must do themselves. They should also offer help to students who cannot access the same tool. Some students may need support with reading or language before they can show a science idea. The teacher should consider these needs when planning the task. A fair lesson does not assume that everyone begins with the same access or skills."),
                        ("A11", "A short learning note can make AI use easier to discuss. Students can record their first idea, the help they requested, one claim they checked, and one change they made. Ms. Lee can use these notes to ask better questions. The notes are useful for feedback, but they are not proof of understanding on their own. Students can fill in a form without thinking deeply."),
                    ]),
                    ("6. Plan for risk and evidence", [
                        ("A12", "A strong answer is not always a sign of strong understanding. Maya may submit a clear paragraph after using AI, but Ms. Lee still needs to know whether Maya understands the filter. The teacher can ask a new question or request a short explanation with the AI window closed. The check should match the learning goal. Good teaching plans the support and the check together."),
                        ("A13", "AI can make teaching more flexible when teachers protect time for student thinking. The next question is what happens when help becomes a habit of avoiding effort. Article B examines that risk. Article C then asks how a teacher can collect evidence of learning. Together, the three articles suggest a simple principle: use AI to support practice, and use suitable checks to decide what students have learned."),
                    ]),
                ],
                "connections": [
                    ("A05 > B08 > C04", "A first attempt connects to an independent check."),
                    ("A08 > B06 > C06", "Explaining in one's own words reveals missing ideas."),
                    ("A12 > B04 > C03", "A polished product can hide weak understanding."),
                ],
            },
        ],
    },
    {
        "id": "B",
        "number": 2,
        "file": "02_When_Help_Becomes_Dependence.pdf",
        "title": ["When Help Becomes", "Dependence"],
        "subtitle": "Student Overuse of AI",
        "short": "When Help Becomes Dependence",
        "accent": "#95602D",
        "tint": "#FCF5EC",
        "focus": "RISK",
        "abstract": (
            "AI can become a habit that replaces student effort. The problem is "
            "not simply how often students open a tool. The problem is whether they "
            "still make choices, check claims, and explain ideas. This article "
            "continues the fictional water-filter lesson from Article A. It describes "
            "signs of dependence and offers classroom routines that help students "
            "return to active learning."
        ),
        "pages": [
            {
                "heading": None,
                "sections": [
                    ("1. When useful help takes over", [
                        ("B01", "AI should support student thinking, not replace it. Yet a student may begin by asking for one hint and later ask the tool to complete every step. In this article, dependence means relying on AI so much that the student avoids important thinking or cannot continue without it. The concern is about the student's role in learning, not about a fixed number of prompts."),
                        ("B02", "Frequent use is not enough to show dependence. A student may use AI many times to practice a language and still make careful choices. Another student may copy one full answer and do very little thinking. Teachers should ask what the tool did and what the student did. The same tool can support active practice in one task and replace it in another."),
                    ]),
                    ("2. A finished answer can hide a problem", [
                        ("B03", "Return to Ms. Lee's fictional water-filter lesson. Imagine that Maya skips her prediction and asks AI to write the whole report. She copies a clear explanation and adds a neat diagram. The work looks complete. However, Maya has not compared the AI claims with the class reading or the test. The steps designed to build understanding have become steps for finishing a document."),
                        ("B04", "A strong answer is not always a sign of strong understanding. When Ms. Lee asks why clear water may still be unsafe, Maya repeats a sentence but cannot explain it. Her report shows what the tool can produce. It gives limited evidence of what she can explain. This fictional example does not prove that all AI use harms learning; it shows why product quality alone can mislead a teacher."),
                    ]),
                ],
            },
            {
                "heading": "Notice what students stop doing",
                "sections": [
                    ("3. Signs that need a conversation", [
                        ("B05", "One warning sign is asking AI before reading the question or making any attempt. Another is accepting every suggestion without checking it. A student may also stop when the tool is unavailable, even on a task that matches earlier practice. These signs should begin a conversation. A single difficult moment may have another cause, such as confusing instructions or a gap in earlier learning."),
                        ("B06", "Students should explain an idea in their own words. A useful follow-up is, 'Why did you choose this answer?' If a student can only repeat the AI text, the teacher should ask which part is unclear. Reading difficulty, stress, or limited language skills may also affect the answer. The aim is to find the next learning step, rather than label the student from one response."),
                        ("B07", "Dependence can grow when students value speed more than understanding. A long task, an unclear goal, or pressure to submit perfect work may make copying feel reasonable. Teachers should examine the task as well as student behavior. If only the final answer receives attention, students may see little reason to show their thinking. Feedback on questions, choices, and revisions can change that message."),
                    ]),
                    ("4. Put student effort back into the routine", [
                        ("B08", "Students should first make an attempt without AI. Ms. Lee can ask for a brief prediction before students open the tool. The first attempt should be small enough that students can begin. It should also be safe to make a mistake. If every early error leads to a lower grade, students may hide their ideas and return to copying a confident answer."),
                        ("B09", "The teacher can then offer a help ladder. First, students reread the task or discuss it with a partner. Next, they ask AI for a hint or an example. They request a full worked example only when it serves the lesson. After receiving help, they close the answer and try a similar task. The goal is to use support in ways that build later independence."),
                    ]),
                ],
                "callout": ("THE SHARED ROUTINE", "Think > Ask > Check > Explain", "Dependence grows when the tool takes over these actions."),
            },
            {
                "heading": "Reduce dependence through better practice",
                "sections": [
                    ("5. Make help visible and useful", [
                        ("B10", "Short pauses for independent work can help students notice what they understand. After AI explains the filter, Maya can draw it from memory and add a reason for each part. She then compares her drawing with the class material. This pause is a chance to learn. It should not automatically become a high-pressure test or remove support that a student needs to access the task."),
                        ("B11", "Students can also keep a short note about the help they used. Maya records, 'I asked for a hint, checked one claim, and changed my explanation.' Ms. Lee can discuss whether the help made Maya more able to continue. A long prompt history is not necessary for every lesson. A small, useful record is easier to review and can encourage honest discussion about both success and confusion."),
                    ]),
                    ("6. Check progress toward independence", [
                        ("B12", "A rule against all AI use would not by itself teach students how to use help well. Clear limits can be useful, but students also need models, practice, and feedback. Ms. Lee can gradually reduce hints as Maya becomes more confident. Students who still struggle may need more teaching or a different example. Giving less support too early can create frustration instead of independence."),
                        ("B13", "The key question is whether students become more able to explain and solve problems after receiving help. Completing more assignments does not answer that question. Article C describes short explanations, new tasks, and later checks that can reveal learning. These checks also help the teacher decide when to reduce AI help and when to provide more instruction. Independence is a learning goal that needs evidence over time."),
                    ]),
                ],
                "connections": [
                    ("A05 > B08 > C04", "Trying first makes later independence easier to discuss."),
                    ("A08 > B06 > C06", "An explanation helps locate the idea that needs teaching."),
                    ("A12 > B04 > C03", "Task completion and student learning need separate evidence."),
                ],
            },
        ],
    },
    {
        "id": "C",
        "number": 3,
        "file": "03_Beyond_AI_Use_Checking_Real_Learning.pdf",
        "title": ["Beyond AI Use"],
        "subtitle": "Checking What Students Really Learn",
        "short": "Beyond AI Use",
        "accent": "#535CA3",
        "tint": "#F2F3FA",
        "focus": "EVIDENCE",
        "abstract": (
            "Using AI does not show that a student has learned. A teacher needs "
            "evidence that matches the learning goal. This article continues the "
            "fictional water-filter lesson and presents a simple plan: check the "
            "starting point, ask for an explanation, try a new task, and check again "
            "later. The results should guide feedback and further teaching, not "
            "just produce a score."
        ),
        "pages": [
            {
                "heading": None,
                "sections": [
                    ("1. Separate activity from learning", [
                        ("C01", "A student may use AI for an hour, finish a worksheet, and submit a clear report. These actions show participation and task completion. They do not, by themselves, show understanding. Learning is easier to judge when students explain a reason, use an idea in a new situation, or remember it later. Teachers should decide which of these actions would give useful evidence for the lesson."),
                        ("C02", "In Ms. Lee's fictional science class, the goal is to explain what a simple water filter can and cannot remove. A suitable check asks about those limits. It should not mainly reward a beautiful diagram or advanced English. Students may answer with a short explanation, a labeled drawing, or a conversation. The form can vary while the science idea being checked remains clear."),
                    ]),
                    ("2. Begin with a small comparison", [
                        ("C03", "A strong answer is not always a sign of strong understanding. Maya's AI-assisted report may be useful practice, but Ms. Lee needs more evidence before judging Maya's learning. She should consider the report together with Maya's own explanation and response to a new question. No single task gives a complete picture. Several small checks can reveal both progress and ideas that still need attention."),
                        ("C04", "Students should first make an attempt without AI. Before the lesson, Ms. Lee asks, 'If water looks clear after filtering, is it safe to drink? Explain your answer.' After practice, she asks a similar question. Comparing the reasons can reveal a change in thinking. The questions should be similar in difficulty, and students should receive any usual support that does not supply the science answer."),
                    ]),
                ],
            },
            {
                "heading": "Gather evidence of understanding",
                "sections": [
                    ("3. Ask, explain, and apply", [
                        ("C05", "For a short independent check, Ms. Lee asks students to close the AI answer and explain the filter's limits. The tool should not supply the target explanation during this check. However, language or access support may still be appropriate. The teacher should make the conditions clear in advance. The purpose is to see the student's science thinking, not to create a surprise rule about tools."),
                        ("C06", "Students should explain an idea in their own words. Ms. Lee asks Maya, 'Why can clear water still be unsafe?' She may follow with, 'What does your test show, and what does it not show?' Maya can speak, write, or use a labeled drawing. A useful explanation includes a reason. Repeating the words 'clear is not safe' without a reason gives only limited evidence of understanding."),
                        ("C07", "A new task checks whether students can use an idea beyond the example they practiced. Ms. Lee describes two water samples: one looks dirty, and one looks clear. She asks whether appearance alone can show which is safe. Students must use the same idea in a different situation. The task should change the surface details without adding knowledge that the class has not yet studied."),
                    ]),
                    ("4. Check again after some time", [
                        ("C08", "A later check can show whether an idea lasts beyond the lesson. Several days later, Ms. Lee gives a short question without showing the earlier AI answer. Students explain why a simple filter may not make water safe. This is a check of what they remember and understand at that time. It should be brief enough to fit normal teaching and provide a useful next step."),
                        ("C09", "Ms. Lee can judge each response using three simple questions: Is the main idea correct? Is there a clear reason? Can the student use the idea in a new case? She should keep these parts separate when giving feedback. A student may know the main idea but struggle with a new case. A single total score could hide this difference and make the next teaching step less clear."),
                    ]),
                ],
                "callout": ("A SIMPLE CHECKING PLAN", "Starting point > Explanation > New task > Later check", "Compare the evidence with the original learning goal."),
            },
            {
                "heading": "Use the evidence to improve teaching",
                "sections": [
                    ("5. Respond to what students can show", [
                        ("C10", "Consider three possible patterns in this fictional lesson. A clear report followed by a weak explanation suggests that more checking and teaching are needed. A clear explanation followed by difficulty with a new task suggests a need for varied practice. A good answer today followed by a weak later answer suggests a need to revisit the idea. These patterns guide action; they do not explain every cause by themselves."),
                        ("C11", "Feedback should lead to another chance to learn. If Maya cannot explain the filter's limits, Ms. Lee can use a simpler example, ask a guiding question, or invite her to compare two explanations. Maya can then revise her answer and try another short check. AI may help during this new practice. The next independent response helps show whether the support has led to stronger understanding."),
                    ]),
                    ("6. Make careful claims about success", [
                        ("C12", "Better answers after a lesson do not prove that AI caused the improvement. Students may also benefit from the teacher, practice, peer discussion, or earlier knowledge. To study AI's effect more carefully, a teacher would need a fair comparison and clear conditions. For an everyday lesson, a modest claim is more useful: these checks show what students can do now and help plan what comes next."),
                        ("C13", "AI use and learning success should be discussed separately. Article A shows how AI may support a lesson. Article B explains how that support can turn into dependence. This article adds the evidence needed to judge learning. The three ideas belong together: plan useful help, protect student thinking, and check understanding. An AI activity succeeds when students gain knowledge or skills they can use beyond the AI answer."),
                    ]),
                ],
                "connections": [
                    ("A05 > B08 > C04", "The first attempt provides a starting point for comparison."),
                    ("A08 > B06 > C06", "An explanation turns a learning routine into visible evidence."),
                    ("A12 > B04 > C03", "Use several checks before judging a polished report."),
                ],
            },
        ],
    },
]


for face, filename in [
    ("Demo", "LiberationSans-Regular.ttf"),
    ("Demo-Bold", "LiberationSans-Bold.ttf"),
    ("Demo-Italic", "LiberationSans-Italic.ttf"),
]:
    pdfmetrics.registerFont(TTFont(face, str(FONT_DIR / filename)))

STYLES = {
    "body": ParagraphStyle("body", fontName="Demo", fontSize=11.5, leading=16.8,
                           textColor=INK, alignment=TA_LEFT, spaceAfter=0),
    "abstract": ParagraphStyle("abstract", fontName="Demo", fontSize=10.3,
                               leading=14.2, textColor=INK),
    "connection": ParagraphStyle("connection", fontName="Demo", fontSize=9.1,
                                 leading=12.1, textColor=INK),
}
AUDIT = []


def draw_text(c, x, top, value, size=10, font="Demo", color=INK):
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawString(x, H - top - size, value)


def draw_paragraph(c, value, top, style="body", x=LEFT, width=WIDTH):
    para = Paragraph(escape(value), STYLES[style])
    _, height = para.wrap(width, H)
    para.drawOn(c, x, H - top - height)
    AUDIT.append({"page": c.getPageNumber(), "top": round(top, 2),
                  "bottom": round(top + height, 2), "text": value[:70]})
    return top + height


def draw_frame(c, paper, page):
    accent = colors.HexColor(paper["accent"])
    c.setFillColor(accent)
    c.rect(0, H - 7, W, 7, fill=1, stroke=0)
    draw_text(c, LEFT, 27, "PAPERREADER  /  AI IN TEACHING", 8.6, "Demo-Bold", MUTED)
    tag = f"ARTICLE {paper['id']}  /  {paper['focus']}"
    c.setFont("Demo-Bold", 8.6)
    c.setFillColor(accent)
    c.drawRightString(W - RIGHT, H - 35.6, tag)
    c.setStrokeColor(RULE)
    c.setLineWidth(0.65)
    c.line(LEFT, H - 49, W - RIGHT, H - 49)
    c.line(LEFT, 42, W - RIGHT, 42)
    draw_text(c, LEFT, H - 33, f"{paper['id']}  |  {paper['short']}", 8.2, "Demo", MUTED)
    c.setFont("Demo", 8.2)
    c.setFillColor(MUTED)
    c.drawRightString(W - RIGHT, 24, f"{page} / 3")


def draw_callout(c, paper, top, label, main, sub):
    accent = colors.HexColor(paper["accent"])
    h = 76
    c.setFillColor(colors.HexColor(paper["tint"]))
    c.roundRect(LEFT, H - top - h, WIDTH, h, 5, fill=1, stroke=0)
    draw_text(c, LEFT + 14, top + 10, label, 8.1, "Demo-Bold", accent)
    main_size = 13.7 if len(main) < 44 else 12.1
    draw_text(c, LEFT + 14, top + 27, main, main_size, "Demo-Bold", accent)
    draw_text(c, LEFT + 14, top + 52, sub, 9.4, "Demo", INK)
    return top + h


def draw_connections(c, paper, top, connections):
    h = 115
    accent = colors.HexColor(paper["accent"])
    c.setFillColor(colors.HexColor(paper["tint"]))
    c.roundRect(LEFT, H - top - h, WIDTH, h, 5, fill=1, stroke=0)
    draw_text(c, LEFT + 13, top + 10, "LINKS ACROSS THE SERIES", 8.5, "Demo-Bold", accent)
    y = top + 28
    for refs, note in connections:
        draw_text(c, LEFT + 13, y, refs, 9.1, "Demo-Bold", accent)
        draw_text(c, LEFT + 13, y + 13, note, 9.1)
        y += 27
    return top + h


def build(paper):
    path = HERE / paper["file"]
    c = canvas.Canvas(str(path), pagesize=A4, pageCompression=1)
    c.setTitle(" ".join(paper["title"]) + ": " + paper["subtitle"])
    c.setAuthor("PaperReader Demo Series")
    c.setSubject("Original demonstration article. Fictional classroom examples; not an empirical study.")
    c.setCreator("PaperReader demonstration materials / ReportLab")
    c.setKeywords("AI, teaching, student thinking, dependence, learning checks, PaperReader")
    accent = colors.HexColor(paper["accent"])
    page_ends = []
    for index, page in enumerate(paper["pages"], 1):
        draw_frame(c, paper, index)
        if index == 1:
            top = 65
            for title_line in paper["title"]:
                draw_text(c, LEFT, top, title_line, 26, "Demo-Bold", accent)
                top += 30
            draw_text(c, LEFT, top + 2, paper["subtitle"], 15, "Demo", INK)
            top += 31
            draw_text(c, LEFT, top, "Demo article | Fictional classroom examples | October 2026", 8.7, "Demo", MUTED)
            top += 23
            draw_text(c, LEFT, top, "ABSTRACT", 8.5, "Demo-Bold", accent)
            top = draw_paragraph(c, paper["abstract"], top + 16, "abstract") + 16
        else:
            draw_text(c, LEFT, 66, page["heading"], 17, "Demo-Bold", accent)
            top = 101

        for heading, paragraphs in page["sections"]:
            draw_text(c, LEFT, top, heading, 12.4, "Demo-Bold", accent)
            top += 24
            for pid, body in paragraphs:
                c.bookmarkPage(pid)
                c.addOutlineEntry(f"{pid} - {body.split('.')[0]}", pid, level=0)
                draw_text(c, 38, top + 2, pid, 8, "Demo-Bold", MUTED)
                top = draw_paragraph(c, body, top) + 12
            top += 5

        if page.get("callout"):
            top = draw_callout(c, paper, top + 5, *page["callout"])
        if page.get("connections"):
            top = draw_connections(c, paper, top + 4, page["connections"])
        if top > H - 60:
            raise ValueError(f"Overflow: article {paper['id']} page {index}: bottom {top:.1f}, limit {H - 60:.1f}")
        page_ends.append(round(top, 1))
        c.showPage()
    c.save()
    reader = PdfReader(path)
    assert len(reader.pages) == 3
    extracted = "\n".join(p.extract_text() for p in reader.pages)
    expected_ids = [pid for page in paper["pages"] for _, paras in page["sections"] for pid, _ in paras]
    for pid in expected_ids:
        assert pid in extracted, (paper["id"], pid)
    assert "\ufffd" not in extracted
    for page in paper["pages"]:
        for _, paras in page["sections"]:
            for pid, body in paras:
                expected = re.sub(r"\s+", " ", body)
                actual = re.sub(r"\s+", " ", extracted)
                assert expected in actual, (paper["id"], pid, "text differs")
    words = len(re.findall(r"\b[\w'-]+\b", paper["abstract"] + " " + " ".join(
        body for page in paper["pages"] for _, paras in page["sections"] for _, body in paras)))
    return {"file": str(path), "pages": 3, "body_words": words,
            "bytes": path.stat().st_size, "content_bottoms_pt": page_ends}


def main():
    QA.mkdir(parents=True, exist_ok=True)
    results = [build(p) for p in PAPERS]
    (QA / "layout_audit.json").write_text(json.dumps(AUDIT, indent=2), encoding="utf-8")
    (QA / "validation.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
