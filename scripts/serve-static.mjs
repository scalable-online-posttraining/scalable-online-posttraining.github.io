import { createReadStream } from "node:fs";
import { stat } from "node:fs/promises";
import { createServer } from "node:http";
import path from "node:path";
import process from "node:process";

const root = path.resolve(process.argv[2] ?? "out");
const port = Number.parseInt(process.argv[3] ?? "4173", 10);
const host = "127.0.0.1";

const mimeTypes = new Map([
  [".css", "text/css; charset=utf-8"],
  [".html", "text/html; charset=utf-8"],
  [".jpeg", "image/jpeg"],
  [".jpg", "image/jpeg"],
  [".js", "text/javascript; charset=utf-8"],
  [".json", "application/json; charset=utf-8"],
  [".mp4", "video/mp4"],
  [".m3u8", "application/vnd.apple.mpegurl"],
  [".ts", "video/mp2t"],
  [".pdf", "application/pdf"],
  [".png", "image/png"],
  [".svg", "image/svg+xml"],
  [".ttf", "font/ttf"],
  [".webp", "image/webp"],
  [".woff", "font/woff"],
  [".woff2", "font/woff2"],
]);

function resolveRequestPath(requestUrl) {
  const pathname = decodeURIComponent(new URL(requestUrl, `http://${host}`).pathname);
  const requested = pathname.endsWith("/") ? `${pathname}index.html` : pathname;
  const filePath = path.resolve(root, `.${requested}`);

  if (filePath !== root && !filePath.startsWith(`${root}${path.sep}`)) {
    return null;
  }

  return filePath;
}

function parseRange(header, size) {
  const match = /^bytes=(\d*)-(\d*)$/.exec(header);
  if (!match || (match[1] === "" && match[2] === "")) return null;

  let start;
  let end;

  if (match[1] === "") {
    const suffixLength = Number.parseInt(match[2], 10);
    if (!Number.isFinite(suffixLength) || suffixLength <= 0) return null;
    start = Math.max(size - suffixLength, 0);
    end = size - 1;
  } else {
    start = Number.parseInt(match[1], 10);
    end = match[2] === "" ? size - 1 : Number.parseInt(match[2], 10);
  }

  if (
    !Number.isFinite(start) ||
    !Number.isFinite(end) ||
    start < 0 ||
    start >= size ||
    end < start
  ) {
    return null;
  }

  return { start, end: Math.min(end, size - 1) };
}

const server = createServer(async (request, response) => {
  try {
    const filePath = resolveRequestPath(request.url ?? "/");
    if (!filePath || !["GET", "HEAD"].includes(request.method ?? "")) {
      response.writeHead(filePath ? 405 : 403).end();
      return;
    }

    const fileStat = await stat(filePath);
    if (!fileStat.isFile()) {
      response.writeHead(404).end();
      return;
    }

    const contentType =
      mimeTypes.get(path.extname(filePath).toLowerCase()) ??
      "application/octet-stream";
    const headers = {
      "Accept-Ranges": "bytes",
      "Cache-Control": "no-cache",
      "Content-Type": contentType,
    };
    const rangeHeader = request.headers.range;

    if (rangeHeader) {
      const range = parseRange(rangeHeader, fileStat.size);
      if (!range) {
        response.writeHead(416, {
          ...headers,
          "Content-Range": `bytes */${fileStat.size}`,
        });
        response.end();
        return;
      }

      const contentLength = range.end - range.start + 1;
      response.writeHead(206, {
        ...headers,
        "Content-Length": contentLength,
        "Content-Range": `bytes ${range.start}-${range.end}/${fileStat.size}`,
      });

      if (request.method === "HEAD") {
        response.end();
      } else {
        createReadStream(filePath, range).pipe(response);
      }
      return;
    }

    response.writeHead(200, {
      ...headers,
      "Content-Length": fileStat.size,
    });

    if (request.method === "HEAD") {
      response.end();
    } else {
      createReadStream(filePath).pipe(response);
    }
  } catch (error) {
    const statusCode =
      error instanceof URIError
        ? 400
        : error && typeof error === "object" && "code" in error && error.code === "ENOENT"
          ? 404
          : 500;
    response.writeHead(statusCode).end();
  }
});

server.listen(port, host, () => {
  process.stdout.write(`Local preview: http://${host}:${port}\n`);
});
