package com.gathin.tvhome;

import android.graphics.Canvas;
import android.graphics.ColorFilter;
import android.graphics.Matrix;
import android.graphics.Paint;
import android.graphics.PixelFormat;
import android.graphics.RadialGradient;
import android.graphics.Rect;
import android.graphics.Shader;
import android.graphics.drawable.Drawable;

/**
 * The "Horizon" background: one static elliptical radial gradient, deep blue at the centre falling to
 * near-black at the edges.
 *
 * <p>Why a Drawable and not a {@code GradientDrawable}: on SDK 28 a {@code GradientDrawable} takes only
 * three colours, and per-stop offsets need API 29. This needs five stops at set positions, so it draws a
 * {@link RadialGradient} itself.
 *
 * <p>Why not a bitmap: a 1280x720 wallpaper costs 4 MB in RGB_565 and 8 MB in true colour. A shader costs
 * the paint and nothing else, and on a weak GPU (Amlogic txlx) it is one full-screen fill with no blur,
 * no overdraw layer and no allocation per frame.
 *
 * <p>It never animates. The shader is rebuilt only when the bounds change, which on a TV means once.
 */
final class HorizonBackground extends Drawable {

    /** Centre of the ellipse, as a fraction of width and height. */
    private static final float CENTRE_X = 0.42f;
    private static final float CENTRE_Y = 0.42f;
    /** Radii, as a fraction of width and height. The vertical radius is larger, so the pool is upright. */
    private static final float RADIUS_X = 0.62f;
    private static final float RADIUS_Y = 1.05f;

    private static final int[] COLOURS = {
            0xFF1F45F0,
            0xFF1533C8,
            0xFF0C1F86,
            0xFF060D3A,
            0xFF02040F,
    };
    private static final float[] STOPS = {0f, 0.28f, 0.55f, 0.80f, 1f};

    private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private int builtForWidth = -1;
    private int builtForHeight = -1;

    @Override
    protected void onBoundsChange(Rect bounds) {
        super.onBoundsChange(bounds);
        build(bounds.width(), bounds.height());
    }

    private void build(int width, int height) {
        if (width <= 0 || height <= 0) return;
        if (width == builtForWidth && height == builtForHeight) return;
        builtForWidth = width;
        builtForHeight = height;

        float cx = width * CENTRE_X;
        float cy = height * CENTRE_Y;
        float rx = width * RADIUS_X;
        float ry = height * RADIUS_Y;

        // RadialGradient is always circular, so build it at the horizontal radius and scale the shader
        // vertically about the centre to stretch that circle into the ellipse the design asks for.
        RadialGradient gradient =
                new RadialGradient(cx, cy, rx, COLOURS, STOPS, Shader.TileMode.CLAMP);
        Matrix matrix = new Matrix();
        matrix.setScale(1f, ry / rx, cx, cy);
        gradient.setLocalMatrix(matrix);
        paint.setShader(gradient);
    }

    @Override
    public void draw(Canvas canvas) {
        Rect b = getBounds();
        if (b.isEmpty()) return;
        // A window background can be drawn before onBoundsChange on some builds; build on demand so the
        // first frame is never the plain paint.
        build(b.width(), b.height());
        if (paint.getShader() == null) return;
        canvas.drawRect(b, paint);
    }

    /** The darkest stop, for anything that needs a matching flat colour behind it. */
    static int edgeColour() {
        return COLOURS[COLOURS.length - 1];
    }

    @Override
    public void setAlpha(int alpha) {
        if (paint.getAlpha() != alpha) {
            paint.setAlpha(alpha);
            invalidateSelf();
        }
    }

    @Override
    public void setColorFilter(ColorFilter colorFilter) {
        paint.setColorFilter(colorFilter);
        invalidateSelf();
    }

    @Override
    public int getOpacity() {
        return PixelFormat.OPAQUE;
    }
}
