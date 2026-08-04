(() => {
  function parseBlock(block) {
    const lines = block.split(/\r?\n/);
    let eventName = "message";
    const dataLines = [];

    for (const line of lines) {
      if (line.startsWith("event:")) {
        eventName = line.slice(6).trim() || "message";
        continue;
      }
      if (line.startsWith("data:")) {
        dataLines.push(line.slice(5).trimStart());
      }
    }

    const rawData = dataLines.join("\n");
    if (!rawData) {
      return { event: eventName, data: null, rawData: "" };
    }

    try {
      return { event: eventName, data: JSON.parse(rawData), rawData };
    } catch {
      return { event: eventName, data: rawData, rawData };
    }
  }

  async function stream(response, handlers = {}) {
    if (!response?.body) {
      throw new Error("Streaming response body is not available.");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const blocks = buffer.split(/\n\n/);
      buffer = blocks.pop() || "";

      for (const block of blocks) {
        if (!block.trim()) continue;
        const parsed = parseBlock(block);
        if (parsed.event === "error") {
          handlers.onError?.(parsed.data);
        } else if (parsed.event === "meta") {
          handlers.onMeta?.(parsed.data);
        } else if (parsed.event === "done") {
          handlers.onDone?.(parsed.data);
        } else {
          handlers.onChunk?.(parsed.data);
        }
      }
    }
  }

  window.ChatSSE = { parseBlock, stream };
})();
