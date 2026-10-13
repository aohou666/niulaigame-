package com.local.offlinereplica;

import android.app.Activity;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.view.View;
import android.webkit.CookieManager;
import android.webkit.RenderProcessGoneDetail;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.widget.TextView;

public final class MainActivity extends Activity {
    private static final String GAME_URL = "http://127.0.0.1:8787/index_bh_lite3zbtest_andr.html?mode=main";
    private WebView webView;
    private TextView statusView;
    private boolean mainLoadFailed;
    private AssetHttpServer assetServer;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        enterFullscreen();

        String requestedUrl = getIntent().getStringExtra("startUrl");
        boolean useComputerServer = requestedUrl != null
                && requestedUrl.startsWith("http://127.0.0.1:8788/");
        if (!useComputerServer) {
            requestedUrl = GAME_URL;
            assetServer = new AssetHttpServer(this);
            try {
                assetServer.start();
            } catch (Exception error) {
                throw new IllegalStateException("无法启动内置资源服务", error);
            }
        }

        FrameLayout root = new FrameLayout(this);
        root.setBackgroundColor(0xff080b10);

        webView = new WebView(this);
        root.addView(webView, new FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT));

        statusView = new TextView(this);
        statusView.setTextColor(0xfff0d8a6);
        statusView.setTextSize(16);
        statusView.setGravity(android.view.Gravity.CENTER);
        statusView.setPadding(36, 36, 36, 36);
        statusView.setBackgroundColor(0xff080b10);
        statusView.setText("正在连接本地游戏资源……");
        root.addView(statusView, new FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT));

        setContentView(root);
        configureWebView();
        webView.loadUrl(requestedUrl);
    }

    private void configureWebView() {
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        // All files are packaged in the APK. Reload them from the embedded
        // server so an upgraded build never keeps stale HTML or art assets.
        settings.setCacheMode(WebSettings.LOAD_NO_CACHE);
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(true);
        CookieManager.getInstance().setAcceptCookie(true);
        CookieManager.getInstance().setAcceptThirdPartyCookies(webView, true);

        webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageStarted(WebView view, String url, Bitmap favicon) {
                mainLoadFailed = false;
                statusView.setVisibility(View.VISIBLE);
                statusView.setText("正在载入本地游戏……");
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                if (!mainLoadFailed) {
                    statusView.setVisibility(View.GONE);
                }
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) {
                    mainLoadFailed = true;
                    statusView.setVisibility(View.VISIBLE);
                    statusView.setText("内置游戏资源载入失败。\n\n请点按屏幕重试。");
                    statusView.setOnClickListener(v -> webView.reload());
                }
            }

            @Override
            public boolean onRenderProcessGone(WebView view, RenderProcessGoneDetail detail) {
                recreate();
                return true;
            }
        });
    }

    private void enterFullscreen() {
        getWindow().getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_FULLSCREEN
                        | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                        | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                        | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                        | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                        | View.SYSTEM_UI_FLAG_LAYOUT_STABLE);
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) enterFullscreen();
    }

    @Override
    public void onBackPressed() {
        if (webView != null && webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onDestroy() {
        if (webView != null) {
            webView.destroy();
            webView = null;
        }
        if (assetServer != null) {
            assetServer.stop();
            assetServer = null;
        }
        super.onDestroy();
    }
}
