package com.local.offlinereplica;

import android.content.Context;
import android.content.res.AssetFileDescriptor;
import android.content.res.AssetManager;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedInputStream;
import java.io.BufferedOutputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.nio.file.AtomicMoveNotSupportedException;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

final class AssetHttpServer {
    private static final Set<String> TRAIN_MODULES = new HashSet<>(Arrays.asList(
            "champion", "newChampion", "seasonArena", "spectralTower", "trialBoss", "dojo",
            "teamExpedition", "battleBridge", "risk", "peakWar", "worldKing", "raceTower",
            "stormWar", "eightDiagram", "newSeasonArena", "fairArena", "abyssMaze", "abyssMazeHero"));
    private static final Set<String> TRAIN_PROGRESS_ACTIONS = new HashSet<>(Arrays.asList(
            "challenge", "freedomchallenge", "highladderchallenge", "joinmatching", "championbattle",
            "mopupchallenge", "sweep", "mopup", "knockfloor", "triggerevent", "startgame", "walk",
            "fight", "interact", "passcustoms"));
    private static final Set<String> TRAIN_READ_ACTIONS = new HashSet<>(Arrays.asList(
            "champion", "refresh", "freedomrefresh", "highladderrefresh", "searchteam", "getstormwarplayer"));
    private static final int PORT = 8787;
    private static final int MAX_SAVE_BYTES = 32 * 1024 * 1024;
    private final AssetManager assets;
    private final File saveFile;
    private final Object saveLock = new Object();
    private final ExecutorService workers = Executors.newFixedThreadPool(6);
    private volatile boolean running;
    private ServerSocket serverSocket;
    private Thread acceptThread;

    AssetHttpServer(Context context) {
        this.assets = context.getAssets();
        this.saveFile = new File(context.getFilesDir(), "offline-replica-save.json");
    }

    void start() throws IOException {
        if (running) return;
        serverSocket = new ServerSocket(PORT, 32, InetAddress.getByName("127.0.0.1"));
        running = true;
        acceptThread = new Thread(() -> {
            while (running) {
                try {
                    Socket socket = serverSocket.accept();
                    workers.execute(() -> serve(socket));
                } catch (IOException ignored) {
                    if (!running) break;
                }
            }
        }, "offline-asset-http");
        acceptThread.start();
    }

    void stop() {
        running = false;
        try {
            if (serverSocket != null) serverSocket.close();
        } catch (IOException ignored) {
        }
        workers.shutdownNow();
    }

    private void serve(Socket socket) {
        try (Socket client = socket;
             InputStream requestInput = new BufferedInputStream(client.getInputStream());
             OutputStream raw = new BufferedOutputStream(client.getOutputStream())) {
            client.setSoTimeout(15000);
            String headerBlock = readHeaderBlock(requestInput);
            if (headerBlock == null) return;
            String[] headerLines = headerBlock.split("\\r?\\n");
            String requestLine = headerLines[0];
            String[] request = requestLine.split(" ");
            if (request.length < 2) {
                writeText(raw, 400, "Bad Request");
                return;
            }
            String method = request[0].toUpperCase(Locale.ROOT);
            if (!"GET".equals(method) && !"HEAD".equals(method) && !"POST".equals(method) && !"PUT".equals(method) && !"DELETE".equals(method)) {
                writeText(raw, 405, "Method Not Allowed");
                return;
            }

            Map<String, String> headersMap = new HashMap<>();
            for (int i = 1; i < headerLines.length; i++) {
                String line = headerLines[i];
                int colon = line.indexOf(':');
                if (colon > 0) headersMap.put(line.substring(0, colon).trim().toLowerCase(Locale.ROOT), line.substring(colon + 1).trim());
            }
            String rangeHeader = headersMap.get("range");

            String rawPath = request[1];
            int query = rawPath.indexOf('?');
            if (query >= 0) rawPath = rawPath.substring(0, query);
            String path = URLDecoder.decode(rawPath, StandardCharsets.UTF_8.name());
            while (path.startsWith("/")) path = path.substring(1);
            if ("api/health".equals(path)) {
                writeJson(raw, 200, "{\"ok\":true,\"storage\":\"app-files\"}");
                return;
            }
            if ("api/save".equals(path)) {
                serveSaveApi(method, headersMap, requestInput, raw);
                return;
            }
            if ("api/battle-entities".equals(path)) {
                serveBattleEntitiesApi(method, headersMap, requestInput, raw);
                return;
            }
            if ("api/train-rpc".equals(path)) {
                serveTrainingApi(method, headersMap, requestInput, raw);
                return;
            }
            if ("api/config".equals(path)) {
                writeJson(raw, 200, "{}");
                return;
            }
            if (path.isEmpty()) path = "offline-launcher.html";
            if (path.contains("..") || path.contains("\\")) {
                writeText(raw, 403, "Forbidden");
                return;
            }

            try (AssetFileDescriptor descriptor = assets.openFd(path);
                 InputStream input = new BufferedInputStream(descriptor.createInputStream())) {
                long total = descriptor.getLength();
                long start = 0;
                long end = total - 1;
                boolean partial = false;
                if (rangeHeader != null && rangeHeader.toLowerCase(Locale.ROOT).startsWith("bytes=")) {
                    String[] parts = rangeHeader.substring(6).split("-", 2);
                    if (!parts[0].isEmpty()) start = Math.max(0, Long.parseLong(parts[0]));
                    if (parts.length > 1 && !parts[1].isEmpty()) end = Math.min(end, Long.parseLong(parts[1]));
                    partial = start <= end && start < total;
                }
                if (start > 0) skipFully(input, start);
                long length = end - start + 1;
                StringBuilder headers = new StringBuilder();
                headers.append(partial ? "HTTP/1.1 206 Partial Content\r\n" : "HTTP/1.1 200 OK\r\n");
                headers.append("Content-Type: ").append(mimeType(path)).append("\r\n");
                headers.append("Content-Length: ").append(length).append("\r\n");
                headers.append("Accept-Ranges: bytes\r\n");
                headers.append("Cache-Control: public, max-age=31536000\r\n");
                if (partial) headers.append("Content-Range: bytes ").append(start).append('-').append(end).append('/').append(total).append("\r\n");
                headers.append("Connection: close\r\n\r\n");
                raw.write(headers.toString().getBytes(StandardCharsets.ISO_8859_1));
                if (!"HEAD".equals(method)) copy(input, raw, length);
                raw.flush();
            } catch (Exception notFound) {
                writeText(raw, 404, "Asset not found: " + path);
            }
        } catch (IOException ignored) {
        }
    }

    private void serveSaveApi(String method, Map<String, String> headers, InputStream input, OutputStream output) throws IOException {
        if ("GET".equals(method) || "HEAD".equals(method)) {
            byte[] body;
            synchronized (saveLock) {
                body = saveFile.isFile() ? readFile(saveFile) : "null".getBytes(StandardCharsets.UTF_8);
            }
            writeResponse(output, 200, "OK", "application/json; charset=utf-8", body, !"HEAD".equals(method));
            return;
        }
        if ("DELETE".equals(method)) {
            synchronized (saveLock) {
                if (saveFile.exists() && !saveFile.delete()) throw new IOException("Unable to delete save");
            }
            writeJson(output, 200, "{\"ok\":true}");
            return;
        }
        int length;
        try { length = Integer.parseInt(headers.getOrDefault("content-length", "0")); }
        catch (NumberFormatException error) { writeText(output, 400, "Invalid Content-Length"); return; }
        if (length <= 0 || length > MAX_SAVE_BYTES) {
            writeText(output, 413, "Invalid save size");
            return;
        }
        byte[] body = readExact(input, length);
        String json = new String(body, StandardCharsets.UTF_8).trim();
        if (!(json.startsWith("{") && json.endsWith("}"))) {
            writeText(output, 400, "Save must be a JSON object");
            return;
        }
        synchronized (saveLock) {
            File temporary = new File(saveFile.getParentFile(), saveFile.getName() + ".tmp");
            try (FileOutputStream fileOutput = new FileOutputStream(temporary)) {
                fileOutput.write(body);
                fileOutput.getFD().sync();
            }
            try {
                Files.move(temporary.toPath(), saveFile.toPath(), StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);
            } catch (AtomicMoveNotSupportedException error) {
                Files.move(temporary.toPath(), saveFile.toPath(), StandardCopyOption.REPLACE_EXISTING);
            }
        }
        writeJson(output, 200, "{\"ok\":true,\"bytes\":" + body.length + "}");
    }

    /**
     * Mirrors offline_server.py's battle-entity endpoint. The recovered client
     * asks the local server to normalize magical/mythical-beast entities before
     * it feeds them into the original SBattleTeam/Fight renderer.
     */
    private void serveBattleEntitiesApi(String method, Map<String, String> headers, InputStream input, OutputStream output) throws IOException {
        if (!"POST".equals(method)) {
            writeJson(output, 405, "{\"ok\":false,\"error\":\"Method Not Allowed\"}");
            return;
        }
        try {
            int length = parseContentLength(headers, 2 * 1024 * 1024);
            JSONObject request = new JSONObject(new String(readExact(input, length), StandardCharsets.UTF_8));
            JSONArray sourceEntities = request.optJSONArray("entities");
            if (sourceEntities == null || sourceEntities.length() == 0 || sourceEntities.length() > 4) {
                throw new JSONException("战斗助战实体数量无效");
            }

            JSONArray normalized = new JSONArray();
            Map<Integer, Boolean> usedIds = new HashMap<>();
            for (int index = 0; index < sourceEntities.length(); index++) {
                JSONObject source = sourceEntities.optJSONObject(index);
                if (source == null) throw new JSONException("战斗助战实体必须是对象");
                int entityType = source.optInt("type", 0);
                int entityId = source.optInt("entityId", 0);
                int code = source.optInt("code", 0);
                if ((entityType != 4 && entityType != 5 && entityType != 7) || code <= 0) {
                    throw new JSONException("不允许的战斗助战实体");
                }
                if (entityId < 10000 || entityId > 29999 || usedIds.put(entityId, Boolean.TRUE) != null) {
                    throw new JSONException("战斗助战实体编号无效");
                }

                JSONArray sourceSkills = source.optJSONArray("skillIds");
                JSONArray skillIds = new JSONArray();
                if (sourceSkills != null) {
                    for (int skillIndex = 0; skillIndex < sourceSkills.length(); skillIndex++) {
                        int skillId = sourceSkills.optInt(skillIndex, 0);
                        if (skillId > 0) skillIds.put(skillId);
                    }
                }
                if (skillIds.length() == 0 || skillIds.length() > 16) {
                    throw new JSONException("战斗助战实体技能无效");
                }

                JSONObject attrs = jsonObjectField(source, "attr");
                JSONObject ext = jsonObjectField(source, "ext");
                long lifeMax = Math.max(1L, source.optLong("lifeMax", attrs.optLong("2", 1L)));
                long life = Math.min(lifeMax, Math.max(0L, source.optLong("life", lifeMax)));
                JSONObject entity = new JSONObject();
                entity.put("entityId", entityId);
                entity.put("code", code);
                // SBattleTeam.magical/mythicalBeasts supplies the category. A
                // non-zero value makes the original renderer resolve hero art.
                entity.put("type", 0);
                entity.put("life", life);
                entity.put("lifeMax", lifeMax);
                entity.put("anger", Math.max(0, source.optInt("anger", 0)));
                entity.put("angerMax", Math.max(0, source.optInt("angerMax", 0)));
                entity.put("level", Math.max(1, source.optInt("level", 1)));
                entity.put("dermaCode", Math.max(0, source.optInt("dermaCode", 0)));
                entity.put("trialLevel", Math.max(0, source.optInt("trialLevel", 0)));
                entity.put("raceType", Math.max(1, source.optInt("raceType", 1)));
                entity.put("attr", attrs.toString());
                entity.put("skillIds", skillIds);
                entity.put("ext", ext.toString());
                entity.put("pos", Math.max(0, source.optInt("pos", 0)));
                normalized.put(entity);
            }

            synchronized (saveLock) {
                JSONObject save = saveFile.isFile()
                        ? new JSONObject(new String(readFile(saveFile), StandardCharsets.UTF_8))
                        : new JSONObject();
                save.put("battleEntities", normalized);
                writeSaveBytes(save.toString().getBytes(StandardCharsets.UTF_8));
            }
            JSONObject response = new JSONObject();
            response.put("err", 0);
            response.put("ok", true);
            response.put("local", true);
            response.put("entities", normalized);
            writeJson(output, 200, response.toString());
        } catch (JSONException | IllegalArgumentException error) {
            JSONObject response = new JSONObject();
            try {
                response.put("ok", false);
                response.put("error", error.getMessage() == null ? "本地战斗实体创建失败" : error.getMessage());
            } catch (JSONException impossible) {
                throw new IOException(impossible);
            }
            writeJson(output, 400, response.toString());
        }
    }

    // Keep the phone's training service in sync with offline_server.py. The
    // packaged HTML uses these same transactions on desktop and on the phone.
    private void serveTrainingApi(String method, Map<String, String> headers, InputStream input, OutputStream output) throws IOException {
        try {
            synchronized (saveLock) {
                JSONObject save = saveFile.isFile()
                        ? new JSONObject(new String(readFile(saveFile), StandardCharsets.UTF_8)) : new JSONObject();
                JSONObject training = objectOrCreate(save, "training");
                if ("GET".equals(method)) {
                    writeJson(output, 200, new JSONObject().put("ok", true).put("training", training).toString());
                    return;
                }
                if (!"POST".equals(method)) {
                    writeJson(output, 405, "{\"ok\":false,\"error\":\"Method Not Allowed\"}");
                    return;
                }
                JSONObject request = new JSONObject(new String(readExact(input, parseContentLength(headers, 2 * 1024 * 1024)), StandardCharsets.UTF_8));
                String module = request.optString("module");
                String action = request.optString("action");
                JSONObject data = request.optJSONObject("data");
                if (data == null) data = new JSONObject();
                if (!TRAIN_MODULES.contains(module) || !action.matches("[A-Za-z][A-Za-z0-9]*")) throw new JSONException("不允许的历练本地请求");
                JSONObject state = objectOrCreate(training, module);
                if (!state.has("progress")) state.put("progress", 0);
                if (!state.has("attempts")) state.put("attempts", 0);
                if (!state.has("wins")) state.put("wins", state.optInt("progress"));
                if (!state.has("losses")) state.put("losses", 0);
                JSONObject claims = objectOrCreate(state, "claims");
                JSONObject actions = objectOrCreate(state, "actions");
                JSONObject completed = objectOrCreate(state, "completedBattles");
                JSONArray passed = state.optJSONArray("passed");
                if (passed == null) { passed = new JSONArray(); state.put("passed", passed); }
                boolean verify = data.optBoolean("__verifyOnly");
                boolean progressed = false;
                boolean firstClaim = false;
                String lower = action.toLowerCase(Locale.ROOT);
                boolean mutating = !lower.startsWith("get") && !TRAIN_READ_ACTIONS.contains(lower);
                boolean commit = "commitbattleresult".equals(lower);
                if (!verify) {
                    if (mutating && !commit) actions.put(action, actions.optInt(action) + 1);
                    if (data.optBoolean("__prepareBattle")) {
                        state.put("attempts", state.optInt("attempts") + 1);
                    } else if (commit) {
                        String id = data.optString("battleId").trim();
                        boolean won = data.optBoolean("won");
                        if (!id.isEmpty() && !completed.has(id)) {
                            long now = System.currentTimeMillis() / 1000;
                            completed.put(id, new JSONObject().put("won", won).put("at", now));
                            if (won) {
                                state.put("progress", state.optInt("progress") + 1);
                                state.put("wins", state.optInt("wins") + 1);
                                passed.put(new JSONObject().put("progress", state.optInt("progress")).put("battleId", id).put("at", now));
                                progressed = true;
                            } else state.put("losses", state.optInt("losses") + 1);
                            while (completed.length() > 256) completed.remove(completed.keys().next());
                        }
                    } else if (TRAIN_PROGRESS_ACTIONS.contains(lower)) {
                        state.put("attempts", state.optInt("attempts") + 1);
                        state.put("progress", state.optInt("progress") + 1);
                        state.put("wins", state.optInt("wins") + 1);
                        passed.put(new JSONObject().put("progress", state.optInt("progress")).put("action", action).put("at", System.currentTimeMillis() / 1000));
                        progressed = true;
                    }
                    while (passed.length() > 200) passed.remove(0);
                    if (lower.contains("reward") || lower.contains("achievement")) {
                        String key = data.optString("id", action);
                        firstClaim = !claims.optBoolean(key);
                        claims.put(key, true);
                    }
                    if (mutating) {
                        JSONArray log = training.optJSONArray("rpcLog");
                        if (log == null) { log = new JSONArray(); training.put("rpcLog", log); }
                        log.put(new JSONObject().put("module", module).put("action", action).put("data", data));
                        while (log.length() > 200) log.remove(0);
                        writeSaveBytes(save.toString().getBytes(StandardCharsets.UTF_8));
                    }
                }
                JSONObject response = new JSONObject().put("err", 0).put("ok", true).put("local", true)
                        .put("module", module).put("action", action).put("state", state)
                        .put("progressed", progressed).put("firstClaim", firstClaim);
                if (verify) response.put("verified", true);
                writeJson(output, 200, response.toString());
            }
        } catch (JSONException | IllegalArgumentException error) {
            writeJson(output, 400, "{\"ok\":false,\"error\":" + JSONObject.quote(error.getMessage()) + "}");
        }
    }

    private static JSONObject objectOrCreate(JSONObject parent, String key) throws JSONException {
        JSONObject child = parent.optJSONObject(key);
        if (child == null) { child = new JSONObject(); parent.put(key, child); }
        return child;
    }

    private static int parseContentLength(Map<String, String> headers, int maximum) {
        int length;
        try {
            length = Integer.parseInt(headers.getOrDefault("content-length", "0"));
        } catch (NumberFormatException error) {
            throw new IllegalArgumentException("请求大小无效");
        }
        if (length <= 0 || length > maximum) throw new IllegalArgumentException("请求大小无效");
        return length;
    }

    private static JSONObject jsonObjectField(JSONObject source, String field) throws JSONException {
        Object value = source.opt(field);
        if (value instanceof JSONObject) return (JSONObject) value;
        if (value instanceof String) return new JSONObject((String) value);
        throw new JSONException("战斗助战实体" + field + "无效");
    }

    private void writeSaveBytes(byte[] body) throws IOException {
        File temporary = new File(saveFile.getParentFile(), saveFile.getName() + ".tmp");
        try (FileOutputStream fileOutput = new FileOutputStream(temporary)) {
            fileOutput.write(body);
            fileOutput.getFD().sync();
        }
        try {
            Files.move(temporary.toPath(), saveFile.toPath(), StandardCopyOption.REPLACE_EXISTING, StandardCopyOption.ATOMIC_MOVE);
        } catch (AtomicMoveNotSupportedException error) {
            Files.move(temporary.toPath(), saveFile.toPath(), StandardCopyOption.REPLACE_EXISTING);
        }
    }

    private static String readHeaderBlock(InputStream input) throws IOException {
        ByteArrayOutputStream bytes = new ByteArrayOutputStream();
        int matched = 0;
        while (bytes.size() < 64 * 1024) {
            int value = input.read();
            if (value < 0) return bytes.size() == 0 ? null : bytes.toString(StandardCharsets.ISO_8859_1.name());
            bytes.write(value);
            int[] marker = {13, 10, 13, 10};
            matched = value == marker[matched] ? matched + 1 : (value == 13 ? 1 : 0);
            if (matched == 4) return bytes.toString(StandardCharsets.ISO_8859_1.name());
        }
        throw new IOException("Headers too large");
    }

    private static byte[] readExact(InputStream input, int length) throws IOException {
        byte[] body = new byte[length];
        int offset = 0;
        while (offset < length) {
            int read = input.read(body, offset, length - offset);
            if (read < 0) throw new IOException("Unexpected end of request");
            offset += read;
        }
        return body;
    }

    private static byte[] readFile(File file) throws IOException {
        try (FileInputStream input = new FileInputStream(file); ByteArrayOutputStream output = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[64 * 1024];
            int read;
            while ((read = input.read(buffer)) >= 0) output.write(buffer, 0, read);
            return output.toByteArray();
        }
    }

    private static void writeJson(OutputStream output, int status, String json) throws IOException {
        writeResponse(output, status, "OK", "application/json; charset=utf-8", json.getBytes(StandardCharsets.UTF_8), true);
    }

    private static void writeResponse(OutputStream output, int status, String reason, String contentType, byte[] body, boolean includeBody) throws IOException {
        String header = "HTTP/1.1 " + status + " " + reason + "\r\nContent-Type: " + contentType + "\r\nContent-Length: " + body.length + "\r\nCache-Control: no-store\r\nConnection: close\r\n\r\n";
        output.write(header.getBytes(StandardCharsets.ISO_8859_1));
        if (includeBody) output.write(body);
        output.flush();
    }

    private static void skipFully(InputStream input, long count) throws IOException {
        long remaining = count;
        while (remaining > 0) {
            long skipped = input.skip(remaining);
            if (skipped <= 0) {
                if (input.read() < 0) throw new IOException("Unexpected end of asset");
                skipped = 1;
            }
            remaining -= skipped;
        }
    }

    private static void copy(InputStream input, OutputStream output, long length) throws IOException {
        byte[] buffer = new byte[64 * 1024];
        long remaining = length;
        while (remaining > 0) {
            int read = input.read(buffer, 0, (int) Math.min(buffer.length, remaining));
            if (read < 0) break;
            output.write(buffer, 0, read);
            remaining -= read;
        }
    }

    private static void writeText(OutputStream output, int status, String message) throws IOException {
        byte[] body = message.getBytes(StandardCharsets.UTF_8);
        String header = "HTTP/1.1 " + status + " Error\r\nContent-Type: text/plain; charset=utf-8\r\nContent-Length: " + body.length + "\r\nConnection: close\r\n\r\n";
        output.write(header.getBytes(StandardCharsets.ISO_8859_1));
        output.write(body);
        output.flush();
    }

    private static String mimeType(String path) {
        String lower = path.toLowerCase(Locale.ROOT);
        if (lower.endsWith(".html")) return "text/html; charset=utf-8";
        if (lower.endsWith(".js")) return "application/javascript; charset=utf-8";
        if (lower.endsWith(".json")) return "application/json; charset=utf-8";
        if (lower.endsWith(".png")) return "image/png";
        if (lower.endsWith(".webp")) return "image/webp";
        if (lower.endsWith(".jpg") || lower.endsWith(".jpeg")) return "image/jpeg";
        if (lower.endsWith(".mp3")) return "audio/mpeg";
        if (lower.endsWith(".ttf")) return "font/ttf";
        if (lower.endsWith(".fnt")) return "text/plain; charset=utf-8";
        return "application/octet-stream";
    }
}
