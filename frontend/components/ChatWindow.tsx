import { BASE_URL } from "@/config/constants";
import React, { useState, useEffect, useRef } from "react";
import { trackPromise } from "react-promise-tracker";
import BouncingDots from "./BouncingDots";
import ErrorPopup from "./ErrorPopup";
import MarkdownMessage from "./MarkdownMessage";

export interface Message {
  persona: string;
  message: string;
}

const ChatWindow = () => {
  const [question, setQuestion] = useState<string>("");
  const [userInput, setUserInput] = useState<string>("");
  const [systemResponse, setSystemResponse] = useState<string>("");
  const [backendError, setBackendError] = useState<boolean>(false);
  const chatWindowRef = useRef<HTMLDivElement>(null);

  const handleUserInput = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    setUserInput(event.target.value);
  };

  const handleSendMessage = () => {
    // Check if user has typed a message
    if (userInput) {
      // Add user's message to state
      setQuestion(userInput);
      setUserInput("");
      // generate responses
      generateSystemResponse(userInput);
    }
  };

  const generateSystemResponse = (userInput: string) => {
    const streamRequest = async (userInput: string) => {
      const response = await fetch(BASE_URL + "/getKnowledge", {
        method: "POST",
        mode: "cors",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          q: userInput,
        }),
      });

      if (!response.ok) {
        handleErrorOccured();
        throw new Error("Request failed");
      }
      if (response.body == null) return;
      const reader = response.body.getReader();
      let receivedText = "";

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        const textChunk = new TextDecoder("utf-8").decode(value);
        receivedText += textChunk;
        setSystemResponse(receivedText);
      }
    };

    trackPromise(streamRequest(userInput)).catch((error) => {
      console.error("Error:", error);
    });
  };

  const handleErrorOccured = () => {
    setBackendError(true);
  };

  const handleErrorIgnore = () => {
    setBackendError(false);
  };
  const handleErrorReset = () => {
    setBackendError(false);
    reset();
  };

  function interleaveHistory(user: string[], system: string[]): Message[] {
    let interleavedArr: Message[] = [];
    for (let i = 0; i < user.length; i++) {
      interleavedArr.push({ persona: "user", message: user[i] });
      interleavedArr.push({ persona: "system", message: system[i] });
    }
    return interleavedArr;
  }

  function reset() {
    setQuestion("");
    setUserInput("");
    setSystemResponse("");
  }

  return (
    <div className="chat-window" ref={chatWindowRef}>
      <div className="chat-content">
        <div className="message-list">
          {question != "" ? (
            <button
              className="reset-button message system-message"
              onClick={reset}
            >
              Reset Q&A
            </button>
          ) : (
            ""
          )}
          {question != "" && (
            <div className={`message user-message`}>
              <MarkdownMessage message={question} />
            </div>
          )}
          {question != "" && (
            <div className={`message system-message`}>
              {systemResponse != "" ? (
                <MarkdownMessage message={systemResponse} />
              ) : (
                <BouncingDots />
              )}
            </div>
          )}
        </div>
      </div>
      <div className="input-container">
        <textarea
          className="message-input"
          placeholder="Ask your question here..."
          value={userInput}
          onChange={handleUserInput}
          disabled={question != "" && systemResponse == ""}
          onKeyDown={(event) => {
            if (event.keyCode === 13 && !event.shiftKey) {
              // 13 is the keyCode for the enter key
              event.preventDefault(); // Prevent the default behavior of the enter key
              handleSendMessage();
            }
          }}
        />
        <button className="send-button" onClick={handleSendMessage}>
          Send
        </button>
      </div>
      <ErrorPopup
        error={backendError}
        onIgnore={handleErrorIgnore}
        onReset={handleErrorReset}
      />
    </div>
  );
};

export default ChatWindow;
