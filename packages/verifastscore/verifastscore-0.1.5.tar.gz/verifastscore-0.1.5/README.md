<h1>🔍⚡ VeriFastScore</h1>

<p><strong>VeriFastScore</strong> is a fast and efficient factuality evaluation tool that jointly extracts and verifies fine-grained factual claims from long-form LLM-generated responses, conditioned on evidence collated from google search results retrieved using <a href="https://serper.dev" target="_blank">SERPER</a> API.</p>

<p>This <a href="https://github.com/RishanthRajendhran/VeriFastScore" target="_blank">repository</a> packages VeriFastScore as a pip-installable Python package with a command-line interface (<code>verifastscore</code>), simplifying usage and deployment.</p>
<hr />

<p>Coming soon: Dynamic Batching to further imrpove speedups and add support for multi-GPU usage</p>

<h1>Important Links</h1>
<ul>
  <li>
    <a href="https://arxiv.org/abs/2505.16973" target="_blank">
      Paper
    </a>
  </li> 
  <li>
    <a href="https://huggingface.co/rishanthrajendhran/VeriFastScore" target="_blank">
      Model
    </a>
  </li>
  <li>
    <a href="https://huggingface.co/datasets/rishanthrajendhran/VeriFastScore" target="_blank">
      Dataset
    </a>
  </li>
</ul>

<hr />

<h2>📦 Installation</h2>

<p><strong>VeriFastScore</strong> supports both CPU and GPU setups. Please follow the appropriate instructions below:</p>

<h3>▶️ CPU Installation [Default]</h3>
<p>To install VeriFastScore for CPU-only usage:</p>
<pre><code>pip install verifastscore
python3 -m spacy download en_core_web_sm
</code></pre>

<h3>▶️ GPU Installation (with FlashAttention) [Recommended]</h3>
<p>If you want GPU acceleration with FlashAttention, you must install compatible versions of <code>torch</code> and <code>flash-attn</code> manually before installing <code>verifastscore</code>.</p>

<pre><code># Install CUDA-enabled PyTorch (adjust for your CUDA version)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Install flash-attn (manually, requires build tools and matching CUDA)
pip install flash-attn --no-build-isolation

# Then install verifastscore
pip install verifastscore

# Finally, download the spaCy model
python3 -m spacy download en_core_web_sm
</code></pre>

<h3>▶️ Development install (local)</h3>
<pre><code>git clone https://github.com/rishanthrajendhran/verifastscore.git
cd verifastscore
pip install -e .
python3 -m spacy download en_core_web_sm
</code></pre>

<hr />

<h2>🔐 Set Your SERPER API Key</h2>

<p>VeriFastScore retrieves external evidence using Serper.dev. You'll need to set your API key in the environment:</p>

<h3>💻 Linux/macOS</h3>
<pre><code>export SERPER_KEY_PRIVATE="your-key-here"</code></pre>

<p>Add to <code>~/.bashrc</code> or <code>~/.zshrc</code> for permanence:</p>
<pre><code>echo 'export SERPER_KEY_PRIVATE="your-key-here"' >> ~/.bashrc
source ~/.bashrc
</code></pre>

<h3>🪟 Windows CMD</h3>
<pre><code>set SERPER_KEY_PRIVATE=your-key-here</code></pre>

<h3>🧭 Windows PowerShell</h3>
<pre><code>$env:SERPER_KEY_PRIVATE="your-key-here"</code></pre>

<hr />

<h2>🚀 How to Run VeriFastScore</h2>

<p>Once installed, use the CLI tool:</p>

<pre><code>verifastscore --input_file responses.jsonl</code></pre>

<p>Or with custom arguments:</p>
<pre><code>verifastscore \
  --input_file responses.jsonl \
  --data_dir ./data \
  --output_dir ./outputs \
  --model_name rishanthrajendhran/VeriFastScore \
  --search_res_num 10
</code></pre>

<h3>📌 Script Arguments</h3>

<table>
  <thead>
    <tr><th>Argument</th><th>Type</th><th>Default</th><th>Description</th></tr>
  </thead>
  <tbody>
    <tr><td><code>--input_file</code></td><td>str</td><td><em>required</em></td><td>Input file (.jsonl) in <code>--data_dir</code>.</td></tr>
    <tr><td><code>--data_dir</code></td><td>str</td><td><code>./data</code></td><td>Directory for input files.</td></tr>
    <tr><td><code>--output_dir</code></td><td>str</td><td><code>./data</code></td><td>Where to write outputs.</td></tr>
    <tr><td><code>--cache_dir</code></td><td>str</td><td><code>./data/cache</code></td><td>Directory to store SERPER search cache.</td></tr>
    <tr><td><code>--model_name</code></td><td>str</td><td><code>rishanthrajendhran/VeriFastScore</code></td><td>Hugging Face model name or local path. The default value is the path to the trained VeriFastScore model on HuggingFace. Do not change this path unless you want to test your own model.</td></tr>
    <tr><td><code>--search_res_num</code></td><td>int</td><td><code>10</code></td><td>Evidence snippets per sentence.</td></tr>
  </tbody>
</table>

<hr />

<h2>📥 Input Format</h2>

<p>The input must be a <code>.jsonl</code> file with the following structure:</p>

<pre>{
  ["id": "Optional_string_ID"]
  "response": "The capital of France is Paris.",
  [...]
}</pre>

<p>Place the file in the <code>--data_dir</code> directory.</p>

<p>A sample input file can be found <a href="verifastscore/data/data_sample.jsonl" target="_blank">here</a></p>

<hr />

<h2>📤 Output</h2>

<ul>
  <li><code>./outputs/evidence_*.jsonl</code> – Response with retrieved evidence</li>
  <li><code>./outputs/model_output/decomposition_verification_*.jsonl</code> – Claim-level factuality labels</li>
  <li><code>./outputs/time/verifastscore_time_*.pkl</code> – Timing breakdown</li>
</ul>

<p>Example output:</p>
<pre>"claim_verification_result": [
  {"claim": "Paris is the capital of France.", "verification_result": "supported"},
  {"claim": "France is in South America.", "verification_result": "unsupported"}
]</pre>

<p>Console output will include average VeriFastScore, timing per instance, and per stage.</p>

<hr />

<h2>⚙️ Optional Setup Tools</h2>

<p>To prepare the Python environment:</p>

<ol>
  <li>Clone the repository and create the conda environment:
    <pre><code>conda env create -f environment.yml
conda activate verifastscore</code></pre>
  </li>
  <li>Download spaCy English tokenizer:
    <pre><code>python3 -m spacy download en_core_web_sm</code></pre>
  </li>
  <li>Install PyTorch (choose the version that matches your CUDA setup):
    <pre><code>pip install torch torchvision torchaudio</code></pre>
  </li>
  <li>Install FlashAttention:
    <pre><code>pip install flash-attn --no-build-isolation</code></pre>
  </li>
</ol>

<hr />

<h2>📖 Citation</h2>

<pre><code>
@misc{rajendhran2025verifastscorespeedinglongformfactuality,
      title={VeriFastScore: Speeding up long-form factuality evaluation}, 
      author={Rishanth Rajendhran and Amir Zadeh and Matthew Sarte and Chuan Li and Mohit Iyyer},
      year={2025},
      eprint={2505.16973},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2505.16973}, 
}
</code></pre>

<hr />

<h2>📄 License</h2>

<p>This project is licensed under the <a href="https://www.apache.org/licenses/LICENSE-2.0">Apache 2.0 License</a>.</p>