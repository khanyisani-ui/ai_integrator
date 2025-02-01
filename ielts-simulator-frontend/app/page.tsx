"use client";
import { useState } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export default function IELTSApp() {
  const [transcription, setTranscription] = useState<string>("");
  const [response, setResponse] = useState<string>("");
  const [feedback, setFeedback] = useState<{ [key: string]: any } | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [userInput, setUserInput] = useState<string>("");
  const [mode, setMode] = useState<"practice" | "test">("practice");  // for switching between practice and test mode

  // Record Audio for transcription
  const recordAudio = async () => {
    setLoading(true);
    await axios.post("http://localhost:8000/record_audio/");
    setLoading(false);
    alert("Recording completed!");
  };

  // Transcribe Audio into text
  const transcribeAudio = async () => {
    setLoading(true);
    const res = await axios.post<{ transcription: string }>("http://localhost:8000/transcribe_audio/");
    setTranscription(res.data.transcription);
    setUserInput(res.data.transcription);  // auto-populate input field with transcription
    setLoading(false);
  };

  // Generate AI Response based on user input
  const generateResponse = async () => {
    setLoading(true);
    const res = await axios.post<{ response: string }>("http://localhost:8000/generate_response/", {
      user_input: userInput,
    });
    setResponse(res.data.response);
    setLoading(false);
  };

  // Generate feedback on user input
  const generateFeedback = async () => {
    setLoading(true);
    const res = await axios.post<{ feedback: { [key: string]: any } }>("http://localhost:8000/generate_feedback/", {
      user_input: userInput,
    });
    setFeedback(res.data.feedback);
    setLoading(false);
  };

  // Download the PDF Report with feedback
  const downloadReport = async () => {
    if (!feedback) return;
    await axios
      .post("http://localhost:8000/generate_pdf_report/", feedback, {
        responseType: "blob",
      })
      .then((res) => {
        const url = window.URL.createObjectURL(new Blob([res.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", "IELTS_Report.pdf");
        document.body.appendChild(link);
        link.click();
      });
  };

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-4">
      <h1 className="text-xl font-bold text-center">IELTS Speaking Test Simulator</h1>

      {/* Mode Selection */}
      <div className="flex justify-center space-x-4">
        <Button onClick={() => setMode("practice")}>Practice Mode</Button>
        <Button onClick={() => setMode("test")}>Test Mode</Button>
      </div>

      <div className="flex justify-center space-x-4 mt-4">
        {/* Record Button */}
        <Button onClick={recordAudio} disabled={loading}>Record Audio</Button>
        {/* Transcribe Button */}
        <Button onClick={transcribeAudio} disabled={loading}>Transcribe Audio</Button>
      </div>

      {/* Display Transcription */}
      {transcription && (
        <Card className="mt-4">
          <CardContent>Transcription: {transcription}</CardContent>
        </Card>
      )}

      {/* User Input for AI Response */}
      <Input
        value={userInput}
        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setUserInput(e.target.value)}
        placeholder="Or type your response here..."
        className="mt-4"
      />

      {/* Generate AI Response */}
      <Button onClick={generateResponse} disabled={loading}>Generate AI Response</Button>
      {response && (
        <Card className="mt-4">
          <CardContent>AI Response: {response}</CardContent>
        </Card>
      )}

      {/* Generate Feedback Button */}
      <Button onClick={generateFeedback} disabled={loading}>Generate Feedback</Button>
      {feedback && (
        <Card className="mt-4">
          <CardContent>
            <p>Fluency & Coherence Score: {feedback["Fluency & Coherence"]}</p>
            <p>Lexical Resource Score: {feedback["Lexical Resource"]}</p>
            <p>Pronunciation Feedback: {feedback["Pronunciation Feedback"]}</p>
          </CardContent>
        </Card>
      )}

      {/* Download Report Button */}
      <Button onClick={downloadReport} disabled={!feedback} className="mt-4">Download PDF Report</Button>

      {/* Conditional Content Based on Mode */}
      {mode === "test" && (
        <div className="mt-4">
          <h2>Test Mode: Full IELTS Speaking Test</h2>
          <p>Part 1: Introduction - Answer these basic questions.</p>
          <p>Part 2: Long Turn - Describe a memorable event in your life.</p>
          <p>Part 3: Two-Way Discussion - Discuss an issue in detail.</p>
        </div>
      )}
    </div>
  );
}
