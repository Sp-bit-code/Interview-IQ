import Vapi from "@vapi-ai/web";

const vapiPublicKey =
  import.meta.env.VITE_VAPI_PUBLIC_KEY ||
  import.meta.env.VITE_VAPI_WEB_TOKEN ||
  "";

const isMissingKey = !vapiPublicKey || vapiPublicKey.includes("your_");

if (isMissingKey) {
  console.error(
    "Missing Vapi public key. Add VITE_VAPI_PUBLIC_KEY in .env.local"
  );
}

let vapi = null;

try {
  if (!isMissingKey) {
    vapi = new Vapi(vapiPublicKey);
  }
} catch (error) {
  console.error("Failed to initialize Vapi client:", error);
  vapi = null;
}

export { vapi };