import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./VoiceAssistant.css";

const getUserType = () => String(localStorage.getItem("user_type") || "").trim().toLowerCase();

const routeMap = [
  {
    keywords: ["requirements", "needs", "need list", "ngo requirements", "add requirement", "create requirement"],
    route: (userType) => (userType === "ngo" ? "/ngo-requirements" : "/explore-ngos"),
    response: "Opening the NGO requirements workspace.",
  },
  {
    keywords: ["donations", "review donations", "incoming donations", "donor donations"],
    route: (userType) => (userType === "ngo" ? "/ngo-donations" : "/my-donations"),
    response: "Opening the donation list.",
  },
  {
    keywords: ["allocations", "distribution", "matched donations", "allocation"],
    route: (userType) => (userType === "ngo" ? "/ngo-allocations" : "/dashboard"),
    response: "Opening allocations and matching details.",
  },
  {
    keywords: ["pickup", "pickups", "delivery schedule", "logistics"],
    route: (userType) => (userType === "ngo" ? "/ngo-pickups" : "/my-activity"),
    response: "Opening your pickup and logistics view.",
  },
  {
    keywords: ["analytics", "reports", "insights", "summary"],
    route: (userType) => (userType === "ngo" ? "/ngo-analytics" : "/my-activity"),
    response: "Opening your analytics and summary view.",
  },
  {
    keywords: ["donate", "donation", "give", "contribute", "add donation", "make donation"],
    route: (userType) => (userType === "ngo" ? "/ngo-donations" : "/donate-item"),
    response: userType => (userType === "ngo"
      ? "Opening the NGO donation review page."
      : "Opening the donation page so you can add your item."),
  },
  {
    keywords: ["ngo", "organization", "find ngo", "find ngos", "show ngos", "show organizations"],
    route: "/explore-ngos",
    response: "I found the NGO discovery page for you.",
  },
  {
    keywords: ["history", "my donations", "donation history", "show my donations"],
    route: (userType) => (userType === "ngo" ? "/ngo-donations" : "/my-donations"),
    response: "Opening your donation history.",
  },
  {
    keywords: ["impact", "my impact", "impact report", "show my impact"],
    route: (userType) => (userType === "ngo" ? "/ngo-impact" : "/my-activity"),
    response: "Opening your impact report.",
  },
  {
    keywords: ["dashboard", "home", "main page"],
    route: (userType) => (userType === "ngo" ? "/ngo-dashboard" : "/dashboard"),
    response: "Opening your dashboard.",
  },
  {
    keywords: ["notifications", "notice", "alerts"],
    route: (userType) => (userType === "ngo" ? "/ngo-notifications" : "/notifications"),
    response: "Opening your notifications.",
  },
  {
    keywords: ["profile"],
    route: (userType) => (userType === "ngo" ? "/ngo-profile" : "/profile"),
    response: "Opening your profile.",
  },
];

function buildResponseForCommand(command) {
  const normalized = command.toLowerCase();

  for (const item of routeMap) {
    const match = item.keywords.some((keyword) => normalized.includes(keyword));
    if (!match) continue;

    const userType = getUserType();
    const route = typeof item.route === "function" ? item.route(userType) : item.route;
    const response = typeof item.response === "function" ? item.response(userType) : item.response;

    return {
      route,
      response,
    };
  }

  return {
    route: null,
    response: "I heard you. You can ask me to donate, find NGOs, check your history, or view your impact.",
  };
}

export default function VoiceAssistant() {
  const navigate = useNavigate();
  const recognitionRef = useRef(null);
  const [isOpen, setIsOpen] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [responseText, setResponseText] = useState("Tap the microphone and speak a command.");
  const [error, setError] = useState("");
  const [supported, setSupported] = useState(true);

  const recognitionApi = useMemo(() => {
    return window.SpeechRecognition || window.webkitSpeechRecognition || null;
  }, []);

  useEffect(() => {
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      window.speechSynthesis?.cancel();
    };
  }, []);

  useEffect(() => {
    if (!recognitionApi) {
      setSupported(false);
    }
  }, [recognitionApi]);

  const speakResponse = (text) => {
    if (!("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.lang = "en-US";
    window.speechSynthesis.speak(utterance);
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsListening(false);
  };

  const handleVoiceCommand = (command) => {
    const { route, response } = buildResponseForCommand(command);
    setTranscript(command);

    if (route) {
      setResponseText(response);
      speakResponse(response);
      setTimeout(() => navigate(route), 350);
      return;
    }

    setResponseText(response);
    speakResponse(response);
  };

  const startListening = () => {
    if (!recognitionApi) {
      setError("Speech recognition is not supported in this browser.");
      setResponseText("Voice input is unavailable in this browser.");
      return;
    }

    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }

    const recognition = new recognitionApi();
    recognition.lang = "en-US";
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
      setError("");
      setIsListening(true);
      setResponseText("Listening for your command...");
    };

    recognition.onresult = (event) => {
      const recognizedText = event.results[0][0].transcript;
      handleVoiceCommand(recognizedText);
    };

    recognition.onerror = (event) => {
      const message = event?.error || "Unable to process your voice command.";
      setError(message);
      setResponseText("I could not understand that command. Please try again.");
      setIsListening(false);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;
    recognition.start();
  };
  return (
    <>
      <button
        type="button"
        className="voice-assistant-fab"
        onClick={() => setIsOpen((prev) => !prev)}
        aria-label="Open voice assistant"
      >
        <span className="voice-assistant-fab-icon">🎙️</span>
      </button>

      {isOpen && (
        <div className="voice-assistant-panel" role="dialog" aria-modal="false" aria-label="Voice assistant dialog">
          <div className="voice-assistant-header">
            <div>
              <p className="voice-assistant-kicker">GiveMatch AI</p>
              <h3>Voice Assistant</h3>
            </div>
            <button type="button" className="voice-assistant-close" onClick={() => setIsOpen(false)} aria-label="Close assistant">
              ×
            </button>
          </div>

          <div className="voice-assistant-body">
            <div className="voice-assistant-status">
              <span className={`voice-status-dot ${isListening ? "active" : "idle"}`} />
              <span>{isListening ? "Listening..." : "Ready"}</span>
            </div>

            {error && <div className="voice-assistant-error">{error}</div>}

            <div className="voice-assistant-transcript-box">
              <p className="voice-assistant-label">Heard:</p>
              <p>{transcript || "No speech detected yet."}</p>
            </div>

            <div className="voice-assistant-response-box">
              <p className="voice-assistant-label">Assistant:</p>
              <p>{responseText}</p>
            </div>
          </div>

          <div className="voice-assistant-actions">
            <button
              type="button"
              className={`voice-assistant-action primary ${isListening ? "listening" : ""}`}
              onClick={() => {
                if (isListening) {
                  stopListening();
                  return;
                }
                startListening();
              }}
            >
              {isListening ? "Stop" : "Mic"}
            </button>

            <button type="button" className="voice-assistant-action secondary" onClick={() => setIsOpen(false)}>
              Close
            </button>
          </div>
        </div>
      )}
    </>
  );
}
