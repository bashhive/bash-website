const PUBLIC_FEED_URL = "https://raw.githubusercontent.com/bashhive/bash-website/main/alerts/feed.json";

async function publicFeed(request, env) {
  try {
    const response = await fetch(PUBLIC_FEED_URL, {
      cf: { cacheEverything: true, cacheTtl: 300 },
    });
    if (!response.ok) throw new Error(`GitHub feed returned ${response.status}`);
    return new Response(response.body, {
      headers: {
        "cache-control": "public, max-age=300",
        "content-type": "application/json; charset=utf-8",
      },
    });
  } catch {
    return env.ASSETS.fetch(request);
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/alerts/feed.json") return publicFeed(request, env);
    return env.ASSETS.fetch(request);
  },
};
