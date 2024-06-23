"use client";
import React from "react";

export default function RecordButton() {
  return (
    <button
      className=" cursor-pointer bg-green-50"
      onClick={() => console.log("clicked")}
    >
      <svg
        className="w-48 h-48 text-blue-500"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
      </svg>
    </button>
  );
}
