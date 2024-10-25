import React, { useState } from "react";
import axios from "axios";

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [pdfUrl, setPdfUrl] = useState("");
  const [pdfName, setPdfName] = useState("");
  const [message, setMessage] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleGenerateQrCodes = async () => {
    if (!file) {
      setMessage("Please select a CSV file.");
      return;
    }

    const formData = new FormData();
    formData.append("csv", file);

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/upload",
        formData,
        {
          responseType: "arraybuffer",
        }
      );

      // Create Blob for PDF and set URL
      const pdfBlob = new Blob([response.data], { type: "application/pdf" });
      const url = window.URL.createObjectURL(pdfBlob);
      setPdfUrl(url);

      // Extract the PDF name from the response headers
      const contentDisposition = response.headers["content-disposition"];
      if (
        contentDisposition &&
        contentDisposition.indexOf("filename=") !== -1
      ) {
        const pdfName = contentDisposition
          .split("filename=")[1]
          .replace(/"/g, "")
          .trim();
        setPdfName(pdfName);
      } else {
        setPdfName("generated_qr_code_pdf.pdf");
      }

      setMessage("QR Codes generated successfully!");
    } catch (error) {
      console.error("Error:", error);
      setMessage(
        error.response && error.response.data
          ? `Error: ${error.response.data.error}`
          : "Error generating QR Codes. Please try again."
      );
    }
  };

  const handleDownloadPdf = () => {
    if (pdfUrl) {
      const link = document.createElement("a");
      link.href = pdfUrl;
      link.setAttribute("download", pdfName || "generated_qr_code_pdf.pdf");

      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      setMessage("PDF downloaded successfully!");
    } else {
      setMessage("No PDF available for download.");
    }
  };

  return (
    <div className="bg-blue-50 min-h-screen flex flex-col items-center justify-center">
      <div className="bg-white p-8 rounded-lg shadow-lg w-96 mb-6">
        <h2 className="text-2xl font-bold text-center mb-4 text-gray-800">
          Upload CSV File
        </h2>
        <form className="flex flex-col">
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            className="mb-4 p-2 border border-gray-300 rounded-md"
          />
          <button
            type="button"
            onClick={handleGenerateQrCodes}
            className="bg-blue-500 text-white py-2 rounded-md hover:bg-blue-600 transition duration-200 mb-2"
          >
            Generate QR Codes
          </button>
          <button
            type="button"
            onClick={handleDownloadPdf}
            className="bg-green-500 text-white py-2 rounded-md hover:bg-green-600 transition duration-200"
          >
            Download PDF
          </button>
        </form>
        {message && <p className="mt-4 text-center text-gray-600">{message}</p>}
      </div>
    </div>
  );
};

export default FileUpload;
