let abortController = null;
let acceptedSegments = {}; 
const chatCompletedFlags = {}; // key: segment index, value: boolean
const finalRebuttals = {}; // Store latest edited rebuttals per segment
const lockedChatboxes = {}; // key: index, value: boolean
let toastEditor; // <-- make global


// Show PDF immediately when selected
document.querySelector('input[name="pdf"]').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file && file.type === "application/pdf") {
        const url = URL.createObjectURL(file);
        const viewer = document.getElementById("pdfViewer");
        const container = document.getElementById("pdfViewerContainer");
        viewer.src = url;
        container.style.display = "block";
    }
});

document.getElementById("uploadForm").addEventListener("submit", function(e) {
    e.preventDefault();

    const formData = new FormData(this);
    const submitBtn = document.getElementById("submitBtn");
    const cancelBtn = document.getElementById("cancelBtn");

    // Prepare AbortController for cancel
    abortController = new AbortController();

    // UI feedback
    submitBtn.disabled = true;
    submitBtn.innerText = "Processing...";
    cancelBtn.style.display = "inline-block";

    fetch("/generate", {
        method: "POST",
        body: formData,
        signal: abortController.signal
    })
    .then(res => res.json())
    .then(data => {
        let rebuttalBox = document.getElementById("rebuttalBox");
        if (!rebuttalBox) {
            rebuttalBox = document.createElement("div");
            rebuttalBox.id = "rebuttalBox";
            rebuttalBox.style.margin = "30px auto";
            rebuttalBox.style.maxWidth = "800px";
            document.body.appendChild(rebuttalBox);
        } else {
            rebuttalBox.innerHTML = "";
        }

        const container = document.getElementById("rebuttalBox");
        container.innerHTML = "";
        
        // Render segment-wise rebuttals
        data.segments.forEach((item, index) => {
            const div = document.createElement("div");
            div.className = "rebuttal-segment";
            div.id = `segment-${index}`;
            div.innerHTML = `
                <div class="segment-content" id="segment-content-${index}">
                    <p><strong>Review:</strong> ${item.review}</p>
                    <p><strong>Rebuttal:</strong> ${item.rebuttal}</p>
                </div>
                <button onclick="accept(${index})">Accept</button>
                <button onclick="reject(${index})" data-type="reject" style="background-color:#e74c3c;">Refine</button>
            `;
            container.appendChild(div);
        });
    
        // Create and inject finalRebuttalContainer dynamically if it doesn't exist
        finalContainer = document.getElementById("finalRebuttalContainer");

        if (!finalContainer) {
            finalContainer = document.createElement("div");
            finalContainer.id = "finalRebuttalContainer";

            // Create the consolidate button
            const consolidateBtn = document.createElement("button");
            consolidateBtn.id = "consolidateBtn";
            consolidateBtn.disabled = false;
            consolidateBtn.addEventListener("click", consolidateFinalRebuttal);

            // Final rebuttal box
            const finalBox = document.createElement("div");
            finalBox.id = "finalRebuttalBox";

            // Append children
            finalContainer.appendChild(consolidateBtn);
            finalContainer.appendChild(finalBox);

            // Inject into DOM after chatBox
            const parent = document.getElementById("rebuttalBox");
            parent.parentNode.insertBefore(finalContainer, parent.nextSibling);
        }

        // Render consolidated rebuttal immediately
        const finalBox = document.getElementById("finalRebuttalBox");
        finalBox.innerHTML = `
        <div class="editor-header">
            <h3>Consolidated Rebuttal</h3>
            <p>Edit the final rebuttal below. Markdown formatting supported.</p>
        </div>
        <div id="toastEditor"></div>
        <div class="editor-actions">
            <button id="saveFinalBtn" class="editor-btn">💾 Save</button>
            <button id="copyFinalBtn" class="editor-btn secondary">📋 Copy</button>
        </div>
        `;

        // Initialize Toast UI Editor
        toastEditor = new toastui.Editor({
            el: document.querySelector('#toastEditor'),
            height: '400px',
            initialEditType: 'markdown',
            previewStyle: 'vertical',
            initialValue: data.final_rebuttal,
            usageStatistics: false
        });

        // Save / Copy handlers
        document.getElementById("saveFinalBtn").addEventListener("click", () => {
            const content = toastEditor.getMarkdown();
            const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
            const fileName = "final_rebuttal.md";

            const link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = fileName;

            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        });
        document.getElementById("copyFinalBtn").addEventListener("click", () => {
            const content = toastEditor.getMarkdown();
            navigator.clipboard.writeText(content).then(() => {
                alert("Copied to clipboard!");
            });
        });

        // Enable the consolidate button
        const consolidateBtn = document.getElementById("consolidateBtn");
        consolidateBtn.disabled = false;
        consolidateBtn.innerText = "Regenerate Final Rebuttal";
        consolidateBtn.style.opacity = 1;
    })    
    .catch(err => {
        if (err.name === "AbortError") {
            console.log("Fetch aborted");
        } else {
            console.error("Fetch error:", err);
            alert("Something went wrong. Please try again.");
        }
    })
    .finally(() => {
        // Reset button and hide cancel
        submitBtn.disabled = false;
        submitBtn.innerText = "Generate Rebuttal";
        cancelBtn.style.display = "none";
        abortController = null;
    });
    
});

// Accept the segment
function accept(index) {
    fetch(`/accept/${index}`, { method: "POST" })
        .then(() => {
            const seg = document.getElementById(`segment-content-${index}`);
            seg.style.opacity = 0.5;
            seg.classList.add("accepted");

            const seg_overall = document.getElementById(`segment-${index}`);
            const existingChatbox = document.getElementById(`chatbox-${index}`);

            if (existingChatbox) {
                const paragraphs = seg.querySelectorAll("p");
                if (paragraphs) {
                    const rebuttalParagraph = paragraphs[1]
                    const finalText = existingChatbox.querySelector("p:nth-of-type(2)").textContent.replace(/<\/?p>/g, '').replace(/<br\s*\/?>/gi, '').replace(/^Final Rebuttal:\s*/i, '');
                    if (rebuttalParagraph) {
                        rebuttalParagraph.innerHTML = `<strong>Rebuttal:</strong> ${finalText}`;
                    }
                }
                existingChatbox.remove();
            }
            // Add Accepted label
            const acceptedInnerMsg = seg_overall.querySelector(".accepted-inner-msg");
            if (acceptedInnerMsg) acceptedInnerMsg.remove();
            
            if (!seg_overall.querySelector(".accepted-msg")) {
                const acceptedMsg = document.createElement("p");
                acceptedMsg.className = "accepted-msg";
                acceptedMsg.style.color = "green";
                acceptedMsg.innerHTML = "<strong>Accepted ✔</strong>";
                seg_overall.appendChild(acceptedMsg);
            }

            // Disable Reject button
            const rejectBtn = seg_overall.querySelector(`button[data-type="reject"]`);
            rejectBtn.disabled = true;
            rejectBtn.style.opacity = 0.4;
            
            // Add Edit Again button
            if (!seg_overall.querySelector(`#editAgainBtn-${index}`)) {
                const editAgainBtn = document.createElement("button");
                editAgainBtn.id = `editAgainBtn-${index}`;
                editAgainBtn.innerText = "Edit Again";
                editAgainBtn.style.backgroundColor = "#f39c12";
                editAgainBtn.style.opacity = 1;
                editAgainBtn.style.setProperty("opacity", "1", "important");
                editAgainBtn.onclick = () => editAgain(index);
                editAgainBtn.disabled = false;
                seg_overall.appendChild(editAgainBtn);
            }
            else {
                const editAgainBtn = seg_overall.querySelector(`#editAgainBtn-${index}`);
                editAgainBtn.style.opacity = 1;
                editAgainBtn.disabled = false;
            }

            // Track that this segment is accepted
            acceptedSegments[index] = true;
            
            // Check if all segments are accepted
            checkAllAccepted();
        });
}

document.getElementById("cancelBtn").addEventListener("click", function() {
    if (abortController) {
        abortController.abort();
    }
});


function checkAllAccepted() {
    // Check if all segments are accepted
    const totalSegments = document.querySelectorAll('.rebuttal-segment').length;
    const acceptedCount = Object.values(acceptedSegments).filter(status => status === true).length;

    if (acceptedCount === totalSegments) {
        // Enable Consolidate button
        document.getElementById("consolidateBtn").disabled = false;
        document.getElementById("consolidateBtn").style.opacity = 1;
    }
    else {
        // document.getElementById("consolidateBtn").disabled = true;
        // document.getElementById("consolidateBtn").style.opacity = .5;
    }
}


function editAgain(index) {
    // Restore full opacity
    const seg_overall = document.getElementById(`segment-${index}`);
    seg_overall.style.opacity = 1;
    // seg_overall.style.setProperty("opacity", "1", "important");
    
    const seg = document.getElementById(`segment-content-${index}`);
    
    // Remove Accepted tag
    const acceptedMsg = seg_overall.querySelector(".accepted-msg");
    if (acceptedMsg) acceptedMsg.remove();

    const acceptedInnerMsg = seg_overall.querySelector(".accepted-inner-msg");
    if (acceptedInnerMsg) acceptedInnerMsg.remove();

    // Disable Edit Again button
    const editAgainBtn = document.getElementById(`editAgainBtn-${index}`);
    editAgainBtn.style.opacity = .5;
    document.getElementById(`editAgainBtn-${index}`).disabled = true;

    // Reset acceptedSegments to false
    acceptedSegments[index] = false;
    
    reject(index);
}

// Reject the segment and display chatbox under it
function reject(index) {
    const seg_overall = document.getElementById(`segment-${index}`); 
    const segmentDiv = document.getElementById(`segment-content-${index}`);

    // Disable reject button
    const rejectBtn = seg_overall.querySelector(`button[data-type="reject"]`);
    rejectBtn.disabled = true;
    rejectBtn.style.opacity = 0.4;
    
    if (document.getElementById(`chatbox-${index}`)) return;

    const chatBox = document.createElement("div");
    chatBox.className = "chatbox-inline";
    chatBox.id = `chatbox-${index}`;

    const chatArea = document.createElement("div");
    chatArea.id = `chatflow-${index}`;
    chatArea.className = "chatflow";

    const input = document.createElement("textarea");
    input.id = `chatinput-${index}`;
    input.rows = 2;
    input.placeholder = "Type your reply...";

    const sendBtn = document.createElement("button");
    sendBtn.innerText = "Send";
    sendBtn.style.marginTop = "10px";

    chatBox.appendChild(chatArea);
    chatBox.appendChild(input);
    chatBox.appendChild(sendBtn);
    segmentDiv.appendChild(chatBox);

    // Trigger assistant's first question
    // Add assistant is typing message 
    const workingMsg = document.createElement("p");
    workingMsg.id = `working-${index}`;
    workingMsg.innerHTML = `<strong>Assistant is typing...</strong>`;
    document.getElementById(`chatflow-${index}`).appendChild(workingMsg);

    fetch(`/chat/${index}`, {
        method: "POST",
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: "start" })
    })
    .then(res => res.json())
    .then(data => {
        const workingEl = document.getElementById(`working-${index}`);
        if (workingEl) workingEl.remove();
        addAssistantMessage(index, data.reply);
    });

    sendBtn.onclick = () => {
        const msg = input.value.trim();
        //if (!msg) return;

        addUserMessage(index, msg);
        input.value = "";

        const workingMsg = document.createElement("p");
        workingMsg.id = `working-${index}`;
        workingMsg.innerHTML = `<strong>Assistant is typing...</strong>`;
        document.getElementById(`chatflow-${index}`).appendChild(workingMsg);

        fetch(`/chat/${index}`, {
            method: "POST",
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg })
        })
        .then(res => res.json())
        .then(data => {
            const reply = data.reply;
            
            const workingEl = document.getElementById(`working-${index}`);
            if (workingEl) workingEl.remove();

            if (reply.includes("Final rebuttal:")) {
                lockChatbox(index)

                if (!seg_overall.querySelector(`#editAgainBtn-${index}`)) {
                    const editAgainBtn = document.createElement("button");
                    editAgainBtn.id = `editAgainBtn-${index}`;
                    editAgainBtn.innerText = "Edit Again";
                    editAgainBtn.style.backgroundColor = "#f39c12";
                    editAgainBtn.style.opacity = 1;
                    editAgainBtn.style.setProperty("opacity", "1", "important");
                    editAgainBtn.onclick = () => editAgain(index);
                    editAgainBtn.disabled = false;
                    seg_overall.appendChild(editAgainBtn);
                }
                else {
                    const editAgainBtn = seg_overall.querySelector(`#editAgainBtn-${index}`);
                    editAgainBtn.style.opacity = 1;
                    editAgainBtn.disabled = false;
                }
                
                chatCompletedFlags[index] = true;
                finalRebuttals[index] = reply;

                // Final rebuttal stage
                const editArea = document.createElement("textarea");
                editArea.rows = 5;
                editArea.style.width = "100%";
                editArea.value = reply;
                chatBox.appendChild(editArea);

                const acceptBtn = document.createElement("button");
                acceptBtn.innerText = "Accept Rebuttal";
                acceptBtn.style.marginTop = "10px";
                acceptBtn.onclick = () => {
                    fetch(`/accept/${index}`, { method: "POST" });
                    chatBox.innerHTML = `
                        <p><strong>Final Rebuttal Saved:</strong></p>
                        <p>${editArea.value.replace(/\n/g, "<br>")}</p>
                    `;

                    // Mark visually as accepted
                    // segmentDiv.style.opacity = 0.5;
                    document.getElementById(`chatbox-${index}`).style.opacity = 0.5;
                    // Add Accepted label
                    if (!segmentDiv.querySelector(".accepted-inner-msg")) {
                        const acceptedMsg = document.createElement("p");
                        acceptedMsg.className = "accepted-inner-msg";
                        acceptedMsg.style.color = "green";
                        acceptedMsg.innerHTML = "<strong>Accepted ✔</strong>";
                        segmentDiv.appendChild(acceptedMsg);
                    }
                };

                chatBox.appendChild(acceptBtn);
            } else {
                addAssistantMessage(index, reply);
            }
        });
    };
    // Set acceptedSegments[index] to false when rejecting the segment
    acceptedSegments[index] = false;

    // Update the Consolidate button status
    checkAllAccepted();

    // Mark consolidated rebuttal as outdated
    document.getElementById("consolidateBtn").disabled = false;
    document.getElementById("consolidateBtn").innerText = "Regenerate Final Rebuttal";
}

function lockChatbox(index) {
    lockedChatboxes[index] = true;
    const input = document.getElementById(`chatinput-${index}`);
    const sendBtn = input?.nextSibling;
    if (input) input.disabled = true;
    if (sendBtn) sendBtn.disabled = true;
}

function unlockChatbox(index) {
    lockedChatboxes[index] = false;
    const input = document.getElementById(`chatinput-${index}`);
    const sendBtn = input?.nextSibling;
    if (input) input.disabled = false;
    if (sendBtn) sendBtn.disabled = false;
}

function checkLockTrigger(index, reply) {
    if (reply.includes("LOCK_CHAT")) {
    lockChatbox(index);
    }
}

function addUserMessage(index, text) {
    const div = document.createElement("p");
    div.innerHTML = `<strong>You:</strong> ${text}`;
    document.getElementById(`chatflow-${index}`).appendChild(div);
}

function addAssistantMessage(index, text) {
    const div = document.createElement("p");
    div.innerHTML = `<strong>Assistant:</strong> ${text}`;
    document.getElementById(`chatflow-${index}`).appendChild(div);
}


// Save the new rebuttal and mark it accepted
function saveAndAccept(index) {
    const editedText = document.getElementById(`edit-${index}`).value;

    if (!editedText.trim()) {
        alert("Please write something before accepting.");
        return;
    }

    // Accept the segment (we assume backend logic handles final response content separately)
    fetch(`/accept/${index}`, { method: "POST" });

    // Show a confirmation visually
    const finalBox = document.getElementById(`chatbox-${index}`);
    finalBox.innerHTML = `
        <p><strong>Saved:</strong> ${editedText}</p>
        <p style="color:green;"><strong>Marked as accepted ✔</strong></p>
    `;
    finalBox.parentElement.style.opacity = 0.6;
}

function consolidateFinalRebuttal() {
    const btn = document.getElementById("consolidateBtn");
    const box = document.getElementById("finalRebuttalBox");

    // UI feedback
    //box.innerHTML = "<em>Processing final rebuttal...</em>";
    btn.disabled = true;
    btn.innerText = "Processing...";

    const segments = [];

    const segmentEls = document.getElementsByClassName("segment-content");
    console.log(segmentEls)

    for (let i = 0; i < segmentEls.length; i++) {
        const segDiv = segmentEls[i];

        const reviewP = segDiv.getElementsByTagName("p")[0];
        const rebuttalP = segDiv.getElementsByTagName("p")[1];
        

        const review = reviewP ? reviewP.innerText.replace("Review:", "").trim() : "";
        const rebuttal = rebuttalP ? rebuttalP.innerText.replace("Rebuttal:", "").trim() : "";

        segments.push({ review, rebuttal });
    }

    console.log(segments)

    fetch("/consolidate", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ segments })
        }).then(res => res.json())
        .then(data => {
            // box.innerText = data.final_rebuttal;
            console.log("toastEditor instance:", toastEditor);
            console.log("typeof toastEditor.setMarkdown:", typeof toastEditor.setMarkdown);
            toastEditor.setMarkdown(data.final_rebuttal);
           
        })
        .catch(err => {
            console.error("Consolidation error:", err);
            box.innerHTML = "<span style='color:red;'>Failed to generate final rebuttal. Please try again.</span>";
        })
        .finally(() => {
            btn.disabled = false;
            btn.innerText = "Regenerate Final Rebuttal";
        });
}


