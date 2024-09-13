//% color="#AA278D" weight=100
//% inlineInputMode=inline
namespace neoPixelMatrix {
    let ledstrip: any;
    let height: number;
    let width: number;

    //% block="maak nieuwe matrix met %neopix van %rows pixels breed en %cols hoog met helderheid %brightness"
    //% inlineInputMode=inline
    export function setStripTo(neopix:any, rows: number, cols: number, brightness: number) {
        height = rows;
        width = cols;
        ledstrip = neopix
        ledstrip.setBrightness(brightness);
    }

    //% block="toon veranderingen"
    //% inlineInputMode=inline
    export function show() {
        ledstrip.show();
    }

    //% block="wis alles"
    //% inlineInputMode=inline
    export function clear() {
        ledstrip.clear()
    }

    //% block="maak een rechthoek van ( %x1 , %y1 ) naar ( %x2 , %y2 ) met kleur %color=neopixel_colors opvullen? %fill"
    //% inlineInputMode=inline
    export function rechthoek(x1: number, y1: number, x2: number, y2: number, color: number, fill: boolean = true) {
        let x1n = (x1 < x2) ? x1 : x2;
        let x2n = (x1 > x2) ? x1 : x2;
        let y1n = (y1 < y2) ? y1 : y2;
        let y2n = (y1 > y2) ? y1 : y2;

        if (fill) {
            for (let x: number = x1n; x <= x2n; x++) {
                for (let y: number = y1n; y <= y2n; y++) {
                    setPixel(x, y, color);
                }
            }
        } else {
            line(x1n, y1n, x2n, y1n, color);  // Top side
            line(x2n, y1n, x2n, y2n, color);  // Right side
            line(x2n, y2n, x1n, y2n, color);  // Bottom side
            line(x1n, y2n, x1n, y1n, color);  // Left side
        }
    }

    //% block="kleur pixel op ( %x , %y ) met %color=neopixel_colors"
    //% inlineInputMode=inline
    export function setPixel(x: number, y: number, color: number) {
        ledstrip.setPixelColor(XEnYNaarPixelnummer(x, y), color);
    }

    //% block="vertaal ( %x , %y ) naar pixelnummer"
    //% inlineInputMode=inline
    export function XEnYNaarPixelnummer(x: number, y: number): number {
        if (x % 2 === 0) {
            return x * height + y;
        } else {
            return x * height + (height - 1 - y);
        }
    }

    //% block="maak een lijn van ( %x0 , %y0 ) naar ( %x1 , %y1 ) met de kleur %color=neopixel_colors"
    //% inlineInputMode=inline
    export function line(x0: number, y0: number, x1: number, y1: number, color: number) {
        let dx = Math.abs(x1 - x0);
        let dy = Math.abs(y1 - y0);
        let sx = (x0 < x1) ? 1 : -1;
        let sy = (y0 < y1) ? 1 : -1;
        let err = dx - dy;

        while (true) {
            setPixel(x0, y0, color);
            if (x0 === x1 && y0 === y1) {
                break;
            }

            let e2 = 2 * err;
            if (e2 > -dy) {
                err -= dy;
                x0 += sx;
            }
            if (e2 < dx) {
                err += dx;
                y0 += sy;
            }
        }
    }

    //% block="maak een cirkel met midden op ( %x , %y ) met een straal van %r en de kleur %color=neopixel_colors opvullen? %fill"
    //% inlineInputMode=inline
    export function circle(x: number, y: number, r: number, color: number, fill: boolean = true) {
        if (fill) {
            for (let i = 0; i < Math.PI * 2; i += 0.1) {
                for (let j = 0; j <= r; j++) {
                    let nx: number = Math.round(x + (Math.sin(i) * j));
                    let ny: number = Math.round(y + (Math.cos(i) * j));
                    setPixel(nx, ny, color);
                }
            }
        } else {
            for (let i = 0; i < Math.PI * 2; i += 0.1) {
                let nx: number = Math.round(x + (Math.sin(i) * r));
                let ny: number = Math.round(y + (Math.cos(i) * r));
                setPixel(nx, ny, color);
            }
        }
    }
}