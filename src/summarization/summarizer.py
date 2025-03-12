from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
import logging
from pathlib import Path
import textstat
import json
import torch



# Configure logging
logging.basicConfig(
    filename="logs/summarization.log",
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

# Define model path in "models" directory
MODEL_DIR = Path(__file__).resolve().parent.parent.parent / "models" / "bart-large-cnn"
MODEL_DIR.mkdir(parents=True, exist_ok=True)  # Ensure directory exists


# Check for available device (CUDA or CPU)
device = 0 if torch.cuda.is_available() else -1  # Use device 0 (GPU) if available, otherwise use CPU (-1)


# Load or Download Model
try:
    if not (MODEL_DIR / "config.json").exists():  # Check if the model is already downloaded
        logging.info("Downloading BART model for the first time...")
        summarizer = pipeline("summarization", model="facebook/bart-large-cnn",device=device)
        model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")
        tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
        
        # Save model locally
        model.save_pretrained(MODEL_DIR)
        tokenizer.save_pretrained(MODEL_DIR)
        logging.info("BART model downloaded and saved locally.")
        
    else:
        logging.info("Loading BART model from local storage.")
        summarizer = pipeline("summarization", model=str(MODEL_DIR), tokenizer=str(MODEL_DIR),device=device)
        
except Exception as e:
    logging.error(f"Error loading BART model: {e}")
    print(f"Error loading BART model: {e}")
    summarizer = None


print()

def chunk_text_with_overlap(text, max_words=500, overlap=150):
    """Splits text into overlapping chunks while keeping sentences intact."""
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + max_words
        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        # Move forward but keep some overlap
        start += max_words - overlap  

    return chunks


def summarize_text(text, min_length=50, max_length=200):
    """
    Summarizes text using BART with overlapping chunks and returns summary statistics.
    
    Returns:
        - summary_text (str): Final summarized text.
        - summary_stats (dict): Contains original & summary lengths and compression ratio.
    """
    if not summarizer:
        logging.error("Summarizer pipeline not initialized.")
        return "Summarization model unavailable.", {}

    if not text or len(text.split()) < 50:
        logging.warning("Text too short for summarization.")
        return text, {}

    # Create overlapping chunks
    chunks = chunk_text_with_overlap(text)
    summarized_chunks = []




    try:
        for chunk in chunks:
            summary = summarizer(chunk, min_length=min_length, max_length=max_length, do_sample=False)
            summarized_chunks.append(summary[0]["summary_text"])

        # Join summarized chunks
        summary_text = " ".join(summarized_chunks)

        # Compute statistics
        original_words = len(text.split())
        original_chars = len(text)
        summary_words = len(summary_text.split())
        summary_chars = len(summary_text)
        compression_ratio = round(summary_words / original_words, 2) if original_words else 0

        # Calculate Flesch-Kincaid Grade Level ---->  {The higher the score, the more complex the text}
        fk_grade_level  = textstat.flesch_kincaid_grade(summary_text)

        # Calculate Flesch Reading Ease  ---> (0 ---> 100%) {The higher the score (closer to 100), the easier the text is to read}
        fk_reading_ease = textstat.flesch_reading_ease(summary_text)


        summary_stats = {
            "original_words": original_words,
            "original_chars": original_chars,
            "summary_words": summary_words,
            "summary_chars": summary_chars,
            "compression_ratio": compression_ratio,
            "readability_grade(flesch_kincaid)":fk_grade_level,
            "Reading Ease(fl_reading_ease )":fk_reading_ease
        }

        logging.info("Summarization successful.")
        return summary_text, summary_stats

    except Exception as e:
        logging.error(f"Error during summarization: {e}")
        return "Error summarizing text.", {}

#Test it: 
if __name__ == "__main__" :

    ARTICLE = """Elon Musk lost the latest battle in his lawsuit against OpenAI this week, but a federal judge appears to have given Musk — and others who oppose OpenAI’s for-profit conversion — reasons to be hopeful.
        Musk’s suit against OpenAI, which also names Microsoft and OpenAI CEO Sam Altman as defendants, accuses OpenAI of abandoning its nonprofit mission to ensure its AI research benefits all humanity.
        OpenAI was founded as a nonprofit in 2015 but converted to a “capped-profit” structure in 2019, and now seeks to restructure once more into a public benefit corporation. 
        Musk had sought a preliminary injunction to halt OpenAI’s transition to a for-profit. On Tuesday, a federal judge in Northern California, U.S.
        District Court Judge Yvonne Gonzalez Rogers, denied Musk’s request — yet expressed some jurisprudential concerns about OpenAI’s planned conversion.
        Judge Rogers said in her ruling denying the injunction that “significant and irreparable harm is incurred” when the public’s money is used to fund a nonprofit’s conversion into a for-profit.
        OpenAI’s nonprofit currently has a majority stake in OpenAI’s for-profit operations, and it reportedly stands to receive billions of dollars in compensation as a part of the transition.
        Judge Rogers also noted that several of OpenAI’s co-founders, including Altman and president Greg Brockman, made “foundational commitments” not to use OpenAI “as a vehicle to enrich themselves.”
        In her ruling, Judge Rogers said that the Court is prepared to offer an expedited trial in the fall of 2025 to resolve the corporate restructuring disputes. Marc Toberoff, a lawyer representing Musk,
        told TechCrunch that Musk’s legal team is pleased with the judge’s decision and intends to accept the offer for an expedited trial. 
        OpenAI hasn’t said whether it’ll also accept and did not immediately respond to TechCrunch’s request for comment. Judge Rogers’ comments on OpenAI’s for-profit conversion aren’t exactly good news for the company.
        Tyler Whitmer, a lawyer representing Encode, a nonprofit that filed an amicus brief in the case arguing that OpenAI’s for-profit conversion could jeopardize AI safety,
        told TechCrunch that Judge Rogers’ decision puts a “cloud” of regulatory uncertainty over OpenAI’s board of directors. Attorneys general in California and Delaware are already investigating the transition,
        and the concerns Judge Rogers raised could embolden them to probe more aggressively, Whitmer said. There were some wins for OpenAI in Judge Rogers’ ruling. The evidence Musk’s legal team presented to show that OpenAI breached a contract in accepting around $44 million in donations from Musk, 
        then taking steps to convert to a for-profit, was “insufficient for purposes of the high burden required for a preliminary injunction,” Judge Rogers found. In her ruling, the judge pointed out that some emails submitted as exhibits showed Musk himself considering that OpenAI might become a for-profit company someday.
        Judge Rogers also said that Musk’s AI company, xAI, a plaintiff in the case, failed to demonstrate that it would suffer “irreparable harm” should OpenAI’s for-profit conversion not be enjoined.
        Judge Rogers was also unpersuaded by the plaintiffs’ arguments that OpenAI’s close collaborator and investor, Microsoft, would violate interlocking directorate laws and that Musk has standing under a California provision prohibiting self-dealing.
        Musk, once a key supporter of OpenAI, has positioned himself as one of the company’s greatest adversaries. xAI competes directly with OpenAI in developing frontier AI models,
        and Musk and Altman now find themselves jockeying for legal and political power under a new presidential administration. The stakes are high for OpenAI. The company reportedly needs to complete its for-profit conversion by 2026,
        or some of the capital OpenAI recently raised could convert to debt. At least one former OpenAI employee is fearful of the implications for AI governance should OpenAI successfully complete its transition. 
        Speaking to TechCrunch on the condition of anonymity to protect their future job prospects, the ex-employee said they believe the startup’s conversion could threaten public safety. 
        Part of the motivation behind OpenAI’s nonprofit structure was to ensure that profit motives don’t override its mission: ensuring AI research benefits all of humanity. However, if OpenAI becomes a traditional for-profit company,
        there may be little to stop it from prioritizing profit above all else, the former employee told TechCrunch. The ex-employee added that OpenAI’s nonprofit structure was one of the main reasons they joined the organization. Just a few months from now, 
        it should become clearer how many hurdles OpenAI will have to overcome in its for-profit transition. Regulators, AI safety advocates, and tech investors will be watching with great interest."""

    summary, stats = summarize_text(ARTICLE)
    print("\n**Summary:**\n", summary)
    print("-" * 80)
    print("\n**Summary Stats:**\n", json.dumps(stats, indent=4))

  