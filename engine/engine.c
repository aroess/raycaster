#include <stdio.h>
#include <math.h>

#define D2G M_PI/180

int X_DIM;
int Y_DIM;

int OFFSET_H;
int TEX_ID_H;
float horizontalIntersection(float angle, float beta, int px, int py, int table[]) {
    if (angle == 0.0 || angle == 180.0) return -1.0;

    int Y_COORD = py / 64 * 64, DELTA_Y;
    float X_COORD, DELTA_X;

    if (angle > 0.0 && angle < 180) {
        Y_COORD -=   1;     // Strahl zeigt nach oben
        DELTA_Y  = -64;
        DELTA_X  =  64 / tan(angle * D2G);
    } else {
        Y_COORD +=  64;     // Strahl zeigt nach unten
        DELTA_Y  =  64;
        DELTA_X  = -64 / tan(angle * D2G);
    }

    X_COORD = px + (py - Y_COORD) / tan(angle * D2G);

    // correct pixel
    if (angle > 90.0 && angle < 270.0) X_COORD += 1;

    int Y_INDEX = Y_COORD / 64;
    int X_INDEX = (int)(X_COORD / 64);

    if (X_INDEX > X_DIM-1 || X_INDEX < 0) return -1.0;
    while(table[X_DIM * Y_INDEX + X_INDEX] == 0) {
        Y_COORD += DELTA_Y;
        X_COORD += DELTA_X;
        Y_INDEX = Y_COORD / 64;
        X_INDEX = (int)(X_COORD / 64);
        if (X_INDEX > X_DIM-1 || X_INDEX < 0) return -1.0;
    }

    // compute correct offset
    if (angle < 180 && angle > 0)
        OFFSET_H = (int)(X_COORD) % 64;
    else
        OFFSET_H = 64 - (int)(X_COORD) % 64;

    TEX_ID_H = table[X_DIM * Y_INDEX + X_INDEX];

    return fabs(fabs(py - Y_COORD) / sin(angle * D2G) * cos(beta * D2G)); // + add;
}

int OFFSET_V;
int TEX_ID_V;
float verticalIntersection(float angle, float beta, int px, int py, int table[]) {
    if (angle == 90.0 || angle == 270.0) return -1.0;

    int X_COORD = px / 64 * 64, DELTA_X;
    float Y_COORD, DELTA_Y;

    if (angle < 90.0 || angle > 270.0) {
        X_COORD +=  64;     // Strahl zeigt nach rechts
        DELTA_X  =  64;
        DELTA_Y  = -64 * tan(angle * D2G);

    } else {
        X_COORD -=   1;     // Strahl zeight nach links
        DELTA_X  = -64;
        DELTA_Y  =  64 * tan(angle * D2G);
    }

    Y_COORD = py + (px - X_COORD) * tan(angle * D2G);

     // correct pixel
    if (angle > 0.0 && angle < 180.0) Y_COORD += 1;

    int Y_INDEX = (int)(Y_COORD / 64);
    int X_INDEX = X_COORD / 64;

    if (Y_INDEX > Y_DIM-1 || Y_INDEX < 0) return -1.0;
    while(table[X_DIM * Y_INDEX + X_INDEX] == 0) {
        Y_COORD += DELTA_Y;
        X_COORD += DELTA_X;
        Y_INDEX = (int)(Y_COORD / 64);
        X_INDEX = X_COORD / 64;
        if (Y_INDEX > Y_DIM-1 || Y_INDEX < 0) return -1.0;
    }

    // compute correct offset
    if (angle < 90 || angle > 270)
        OFFSET_V = (int)(Y_COORD) % 64;
    else
        OFFSET_V = 64 - (int)(Y_COORD) % 64;

    TEX_ID_V = table[X_DIM * Y_INDEX + X_INDEX];

    return fabs(fabs(px - X_COORD) / cos(angle * D2G) * cos(beta * D2G));
}

float distanceList[1280]; // 320 * 4

float * render(int *table, int rows, int cols, float px, float py, int pdir) {

    X_DIM = cols;
    Y_DIM = rows;

    px = (int)px;
    py = (int)py;

    float current_angle;
    float step = 60.0 / 320.0;
    float distance;
    float h, v, off;
    int tex, alpha;

    float fov_start = pdir + 30.0;
    if (fov_start > 360) fov_start -= 360;

    int i;
    for (i = 0; i < 320; i++) {
        current_angle = fov_start - i * step;
        if (current_angle < 0) current_angle += 360;

        h = horizontalIntersection(current_angle, 30 - i * step, px, py, table);
        v = verticalIntersection  (current_angle, 30 - i * step, px, py, table);

        if      (h < 0.0)   { distance = v; off = OFFSET_V; tex = TEX_ID_V; alpha = 255;}
        else if (v < 0.0)   { distance = h; off = OFFSET_H; tex = TEX_ID_H; alpha = 200;}
        else if (v < h)     { distance = v; off = OFFSET_V; tex = TEX_ID_V; alpha = 255;}
        else                { distance = h; off = OFFSET_H; tex = TEX_ID_H; alpha = 200;}   

        distanceList[i*4]   = distance;
        distanceList[i*4+1] = off;
        distanceList[i*4+2] = (float)tex;
        distanceList[i*4+3] = (float)alpha;
    }
    return(distanceList);
}
