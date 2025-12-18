use pyo3::prelude::*;
use pyo3::exceptions::PyValueError;
use std::collections::HashMap;
use std::thread;
use std::time::{Duration, Instant};
use std::io::{Write, stdout};
use rand::Rng;

// Color constants
const BLACK: u8 = 30;
const RED: u8 = 31;
const GREEN: u8 = 32;
const YELLOW: u8 = 33;
const BLUE: u8 = 34;
const MAGENTA: u8 = 35;
const CYAN: u8 = 36;
const WHITE: u8 = 37;

const BRIGHT_BLACK: u8 = 90;
const BRIGHT_RED: u8 = 91;
const BRIGHT_GREEN: u8 = 92;
const BRIGHT_YELLOW: u8 = 93;
const BRIGHT_BLUE: u8 = 94;
const BRIGHT_MAGENTA: u8 = 95;
const BRIGHT_CYAN: u8 = 96;
const BRIGHT_WHITE: u8 = 97;

const BG_BLACK: u8 = 40;
const BG_RED: u8 = 41;
const BG_GREEN: u8 = 42;
const BG_YELLOW: u8 = 43;
const BG_BLUE: u8 = 44;
const BG_MAGENTA: u8 = 45;
const BG_CYAN: u8 = 46;
const BG_WHITE: u8 = 47;

const BG_BRIGHT_BLACK: u8 = 100;
const BG_BRIGHT_RED: u8 = 101;
const BG_BRIGHT_GREEN: u8 = 102;
const BG_BRIGHT_YELLOW: u8 = 103;
const BG_BRIGHT_BLUE: u8 = 104;
const BG_BRIGHT_MAGENTA: u8 = 105;
const BG_BRIGHT_CYAN: u8 = 106;
const BG_BRIGHT_WHITE: u8 = 107;

const BOLD: u8 = 1;
const DIM: u8 = 2;
const ITALIC: u8 = 3;
const UNDERLINE: u8 = 4;
const BLINK: u8 = 5;
const RAPID_BLINK: u8 = 6;
const REVERSE: u8 = 7;
const HIDDEN: u8 = 8;
const STRIKETHROUGH: u8 = 9;
const RESET: u8 = 0;

#[pyclass]
struct ColoredText;

#[pymethods]
impl ColoredText{
    #[new]
    fn new() -> Self {
        ColoredText
    }

    // Constants as class attributes
    #[classattr]
    const BLACK: u8 = BLACK;
    #[classattr]
    const RED: u8 = RED;
    #[classattr]
    const GREEN: u8 = GREEN;
    #[classattr]
    const YELLOW: u8 = YELLOW;
    #[classattr]
    const BLUE: u8 = BLUE;
    #[classattr]
    const MAGENTA: u8 = MAGENTA;
    #[classattr]
    const CYAN: u8 = CYAN;
    #[classattr]
    const WHITE: u8 = WHITE;
    
    #[classattr]
    const BRIGHT_BLACK: u8 = BRIGHT_BLACK;
    #[classattr]
    const BRIGHT_RED: u8 = BRIGHT_RED;
    #[classattr]
    const BRIGHT_GREEN: u8 = BRIGHT_GREEN;
    #[classattr]
    const BRIGHT_YELLOW: u8 = BRIGHT_YELLOW;
    #[classattr]
    const BRIGHT_BLUE: u8 = BRIGHT_BLUE;
    #[classattr]
    const BRIGHT_MAGENTA: u8 = BRIGHT_MAGENTA;
    #[classattr]
    const BRIGHT_CYAN: u8 = BRIGHT_CYAN;
    #[classattr]
    const BRIGHT_WHITE: u8 = BRIGHT_WHITE;
    
    #[classattr]
    const BG_BLACK: u8 = BG_BLACK;
    #[classattr]
    const BG_RED: u8 = BG_RED;
    #[classattr]
    const BG_GREEN: u8 = BG_GREEN;
    #[classattr]
    const BG_YELLOW: u8 = BG_YELLOW;
    #[classattr]
    const BG_BLUE: u8 = BG_BLUE;
    #[classattr]
    const BG_MAGENTA: u8 = BG_MAGENTA;
    #[classattr]
    const BG_CYAN: u8 = BG_CYAN;
    #[classattr]
    const BG_WHITE: u8 = BG_WHITE;
    
    #[classattr]
    const BG_BRIGHT_BLACK: u8 = BG_BRIGHT_BLACK;
    #[classattr]
    const BG_BRIGHT_RED: u8 = BG_BRIGHT_RED;
    #[classattr]
    const BG_BRIGHT_GREEN: u8 = BG_BRIGHT_GREEN;
    #[classattr]
    const BG_BRIGHT_YELLOW: u8 = BG_BRIGHT_YELLOW;
    #[classattr]
    const BG_BRIGHT_BLUE: u8 = BG_BRIGHT_BLUE;
    #[classattr]
    const BG_BRIGHT_MAGENTA: u8 = BG_BRIGHT_MAGENTA;
    #[classattr]
    const BG_BRIGHT_CYAN: u8 = BG_BRIGHT_CYAN;
    #[classattr]
    const BG_BRIGHT_WHITE: u8 = BG_BRIGHT_WHITE;
    
    #[classattr]
    const BOLD: u8 = BOLD;
    #[classattr]
    const DIM: u8 = DIM;
    #[classattr]
    const ITALIC: u8 = ITALIC;
    #[classattr]
    const UNDERLINE: u8 = UNDERLINE;
    #[classattr]
    const BLINK: u8 = BLINK;
    #[classattr]
    const RAPID_BLINK: u8 = RAPID_BLINK;
    #[classattr]
    const REVERSE: u8 = REVERSE;
    #[classattr]
    const HIDDEN: u8 = HIDDEN;
    #[classattr]
    const STRIKETHROUGH: u8 = STRIKETHROUGH;
    #[classattr]
    const RESET: u8 = RESET;

    #[staticmethod]
    fn colorize(text: &str, fg_color: Option<u8>, bg_color: Option<u8>, style: Option<u8>) -> String {
        let mut codes = Vec::with_capacity(3);
        
        if let Some(s) = style {
            codes.push(s.to_string());
        }
        if let Some(fg) = fg_color {
            codes.push(fg.to_string());
        }
        if let Some(bg) = bg_color {
            codes.push(bg.to_string());
        }
        
        if codes.is_empty() {
            return text.to_string();
        }
        
        format!("\x1b[{}m{}\x1b[0m", codes.join(";"), text)
    }

    #[staticmethod]
    fn print_colored(text: &str, fg_color: Option<u8>, bg_color: Option<u8>, style: Option<u8>) {
        println!("{}", Self::colorize(text, fg_color, bg_color, style));
    }

    #[staticmethod]
    fn color256(text: &str, color_code: u8, bg_code: Option<u8>, style: Option<u8>) -> String {
        let mut codes = Vec::with_capacity(3);
        
        if let Some(s) = style {
            codes.push(s.to_string());
        }
        codes.push(format!("38;5;{}", color_code));
        if let Some(bg) = bg_code {
            codes.push(format!("48;5;{}", bg));
        }
        
        format!("\x1b[{}m{}\x1b[0m", codes.join(";"), text)
    }

    #[staticmethod]
    fn rgb(text: &str, r: u8, g: u8, b: u8, bg: Option<bool>, style: Option<u8>) -> String {
        let mut codes = Vec::with_capacity(2);
        
        if let Some(s) = style {
            codes.push(s.to_string());
        }
        
        if bg.unwrap_or(false) {
            codes.push(format!("48;2;{};{};{}", r, g, b));
        } else {
            codes.push(format!("38;2;{};{};{}", r, g, b));
        }
        
        format!("\x1b[{}m{}\x1b[0m", codes.join(";"), text)
    }

    #[staticmethod]
    fn rgb_bg(
        text: &str,
        r: u8,
        g: u8,
        b: u8,
        fg_r: Option<u8>,
        fg_g: Option<u8>,
        fg_b: Option<u8>,
        style: Option<u8>,
    ) -> String {
        let mut codes = Vec::with_capacity(3);
        
        if let Some(s) = style {
            codes.push(s.to_string());
        }
        
        if let (Some(fr), Some(fg), Some(fb)) = (fg_r, fg_g, fg_b) {
            codes.push(format!("38;2;{};{};{}", fr, fg, fb));
        }
        
        codes.push(format!("48;2;{};{};{}", r, g, b));
        
        format!("\x1b[{}m{}\x1b[0m", codes.join(";"), text)
    }

    #[staticmethod]
    fn hex_color(text: &str, hex_code: &str, bg: Option<bool>, style: Option<u8>) -> PyResult<String> {
        let hex = hex_code.trim_start_matches('#');
        
        let hex_expanded = if hex.len() == 3 {
            hex.chars()
                .map(|c| format!("{}{}", c, c))
                .collect::<String>()
        } else {
            hex.to_string()
        };
        
        if hex_expanded.len() != 6 {
            return Err(PyValueError::new_err("Invalid hex code. Expected format: #RRGGBB"));
        }
        
        let r = u8::from_str_radix(&hex_expanded[0..2], 16)
            .map_err(|_| PyValueError::new_err("Invalid hex code"))?;
        let g = u8::from_str_radix(&hex_expanded[2..4], 16)
            .map_err(|_| PyValueError::new_err("Invalid hex code"))?;
        let b = u8::from_str_radix(&hex_expanded[4..6], 16)
            .map_err(|_| PyValueError::new_err("Invalid hex code"))?;
        
        Ok(Self::rgb(text, r, g, b, bg, style))
    }

    #[staticmethod]
    fn hex_bg(
        text: &str,
        hex_code: &str,
        fg_hex: Option<&str>,
        style: Option<u8>,
    ) -> PyResult<String> {
        let parse_hex = |hex: &str| -> PyResult<(u8, u8, u8)> {
            let hex = hex.trim_start_matches('#');
            let hex_expanded = if hex.len() == 3 {
                hex.chars()
                    .map(|c| format!("{}{}", c, c))
                    .collect::<String>()
            } else {
                hex.to_string()
            };
            
            if hex_expanded.len() != 6 {
                return Err(PyValueError::new_err("Invalid hex code"));
            }
            
            let r = u8::from_str_radix(&hex_expanded[0..2], 16)?;
            let g = u8::from_str_radix(&hex_expanded[2..4], 16)?;
            let b = u8::from_str_radix(&hex_expanded[4..6], 16)?;
            
            Ok((r, g, b))
        };
        
        let (bg_r, bg_g, bg_b) = parse_hex(hex_code)?;
        
        let (fg_r, fg_g, fg_b) = if let Some(fg) = fg_hex {
            let (r, g, b) = parse_hex(fg)?;
            (Some(r), Some(g), Some(b))
        } else {
            (None, None, None)
        };
        
        Ok(Self::rgb_bg(text, bg_r, bg_g, bg_b, fg_r, fg_g, fg_b, style))
    }

    #[staticmethod]
    fn hsl_to_rgb(h: f64, s: f64, l: f64) -> (u8, u8, u8) {
        let h = h % 360.0;
        let s = s.max(0.0).min(1.0);
        let l = l.max(0.0).min(1.0);
        
        if s == 0.0 {
            let gray = (l * 255.0) as u8;
            return (gray, gray, gray);
        }
        
        let hue_to_rgb = |p: f64, q: f64, mut t: f64| -> f64 {
            if t < 0.0 {
                t += 1.0;
            }
            if t > 1.0 {
                t -= 1.0;
            }
            if t < 1.0 / 6.0 {
                return p + (q - p) * 6.0 * t;
            }
            if t < 1.0 / 2.0 {
                return q;
            }
            if t < 2.0 / 3.0 {
                return p + (q - p) * (2.0 / 3.0 - t) * 6.0;
            }
            p
        };
        
        let q = if l < 0.5 {
            l * (1.0 + s)
        } else {
            l + s - l * s
        };
        let p = 2.0 * l - q;
        
        let r = (hue_to_rgb(p, q, h / 360.0 + 1.0 / 3.0) * 255.0) as u8;
        let g = (hue_to_rgb(p, q, h / 360.0) * 255.0) as u8;
        let b = (hue_to_rgb(p, q, h / 360.0 - 1.0 / 3.0) * 255.0) as u8;
        
        (r, g, b)
    }

    #[staticmethod]
    fn hsl(text: &str, h: f64, s: f64, l: f64, bg: Option<bool>, style: Option<u8>) -> String {
        let (r, g, b) = Self::hsl_to_rgb(h, s, l);
        Self::rgb(text, r, g, b, bg, style)
    }

    #[staticmethod]
    fn hsl_bg(
        text: &str,
        h: f64,
        s: f64,
        l: f64,
        fg_h: Option<f64>,
        fg_s: Option<f64>,
        fg_l: Option<f64>,
        style: Option<u8>,
    ) -> String {
        let (bg_r, bg_g, bg_b) = Self::hsl_to_rgb(h, s, l);
        
        let (fg_r, fg_g, fg_b) = if let (Some(fh), Some(fs), Some(fl)) = (fg_h, fg_s, fg_l) {
            let (r, g, b) = Self::hsl_to_rgb(fh, fs, fl);
            (Some(r), Some(g), Some(b))
        } else {
            (None, None, None)
        };
        
        Self::rgb_bg(text, bg_r, bg_g, bg_b, fg_r, fg_g, fg_b, style)
    }

    #[staticmethod]
    fn from_preset(text: &str, preset_name: &str, style: Option<u8>) -> PyResult<String> {
        let presets = get_color_presets();
        
        let (r, g, b) = presets.get(preset_name).ok_or_else(|| {
            let available: Vec<&str> = presets.keys().map(|s| s.as_str()).collect();
            PyValueError::new_err(format!(
                "Unknown preset '{}'. Available presets: {}",
                preset_name,
                available.join(", ")
            ))
        })?;
        
        Ok(Self::rgb(text, *r, *g, *b, None, style))
    }

    #[staticmethod]
    fn from_theme(text: &str, theme_name: &str) -> PyResult<String> {
        let themes = get_theme_presets();
        
        let theme = themes.get(theme_name).ok_or_else(|| {
            let available: Vec<&str> = themes.keys().map(|s| s.as_str()).collect();
            PyValueError::new_err(format!(
                "Unknown theme '{}'. Available themes: {}",
                theme_name,
                available.join(", ")
            ))
        })?;
        
        Ok(Self::rgb_bg(
            text,
            theme.bg.0,
            theme.bg.1,
            theme.bg.2,
            Some(theme.fg.0),
            Some(theme.fg.1),
            Some(theme.fg.2),
            theme.style,
        ))
    }

    #[staticmethod]
    fn gradient_text(text: &str, start_rgb: (u8, u8, u8), end_rgb: (u8, u8, u8), style: Option<u8>) -> String {
        let chars: Vec<char> = text.chars().collect();
        let len = chars.len();
        
        if len <= 1 {
            return Self::rgb(text, start_rgb.0, start_rgb.1, start_rgb.2, None, style);
        }
        
        let mut result = String::with_capacity(text.len() * 20);
        
        for (i, ch) in chars.iter().enumerate() {
            if ch.is_whitespace() {
                result.push(*ch);
                continue;
            }
            
            let ratio = i as f64 / (len - 1) as f64;
            let r = (start_rgb.0 as f64 + (end_rgb.0 as i16 - start_rgb.0 as i16) as f64 * ratio) as u8;
            let g = (start_rgb.1 as f64 + (end_rgb.1 as i16 - start_rgb.1 as i16) as f64 * ratio) as u8;
            let b = (start_rgb.2 as f64 + (end_rgb.2 as i16 - start_rgb.2 as i16) as f64 * ratio) as u8;
            
            result.push_str(&Self::rgb(&ch.to_string(), r, g, b, None, style));
        }
        
        result
    }

    #[staticmethod]
    fn rainbow(text: &str, style: Option<u8>) -> String {
        let colors = vec![
            (255, 0, 0),
            (255, 127, 0),
            (255, 255, 0),
            (0, 255, 0),
            (0, 0, 255),
            (75, 0, 130),
            (143, 0, 255),
        ];
        
        let mut result = String::with_capacity(text.len() * 20);
        let mut color_idx = 0;
        
        for ch in text.chars() {
            if ch.is_whitespace() {
                result.push(ch);
                continue;
            }
            
            let (r, g, b) = colors[color_idx % colors.len()];
            result.push_str(&Self::rgb(&ch.to_string(), r, g, b, None, style));
            color_idx += 1;
        }
        
        result
    }

    #[staticmethod]
    #[pyo3(signature = (text, animation_type="typing", speed=0.05, cycles=1))]
    fn animate_text(text: &str, animation_type: &str, speed: f64, cycles: usize) {
        match animation_type {
            "typing" => {
                for i in 0..=text.len() {
                    print!("\r{}", &text[..i]);
                    stdout().flush().unwrap();
                    thread::sleep(Duration::from_secs_f64(speed));
                }
                println!();
            }
            "fade_in" => {
                for brightness in (0..=100).step_by(5) {
                    let value = (brightness as f64 * 2.55) as u8;
                    let colored_text = Self::rgb(text, value, value, value, None, None);
                    print!("\r{}", colored_text);
                    stdout().flush().unwrap();
                    thread::sleep(Duration::from_secs_f64(speed));
                }
                println!();
            }
            "blink" => {
                for _ in 0..cycles {
                    print!("\r{}", text);
                    stdout().flush().unwrap();
                    thread::sleep(Duration::from_secs_f64(speed));
                    
                    print!("\r{}", " ".repeat(text.len()));
                    stdout().flush().unwrap();
                    thread::sleep(Duration::from_secs_f64(speed));
                }
                println!("{}", text);
            }
            "rainbow_wave" => {
                let mut hue_offset = 0.0;
                for _ in 0..(cycles * 360) {
                    let mut result = String::with_capacity(text.len() * 20);
                    for (i, ch) in text.chars().enumerate() {
                        if ch.is_whitespace() {
                            result.push(ch);
                            continue;
                        }
                        
                        let hue = (i as f64 * 10.0 + hue_offset) % 360.0;
                        let (r, g, b) = Self::hsl_to_rgb(hue, 1.0, 0.5);
                        result.push_str(&Self::rgb(&ch.to_string(), r, g, b, None, None));
                    }
                    
                    print!("\r{}", result);
                    stdout().flush().unwrap();
                    thread::sleep(Duration::from_secs_f64(speed));
                    hue_offset = (hue_offset + 5.0) % 360.0;
                }
                println!();
            }
            "bounce" => {
                for _ in 0..cycles {
                    let amplitudes: Vec<i32> = (0..5).chain((1..4).rev()).collect();
                    for amplitude in amplitudes {
                        let mut result = String::new();
                        for (i, ch) in text.chars().enumerate() {
                            if ch.is_whitespace() {
                                result.push(ch);
                                continue;
                            }
                            
                            let char_amplitude = amplitude as f64 * (i as f64 / 2.0).sin();
                            let padding = " ".repeat(char_amplitude.abs() as usize);
                            
                            if char_amplitude >= 0.0 {
                                result.push_str(&padding);
                                result.push(ch);
                            } else {
                                result.push(ch);
                                result.push_str(&padding);
                            }
                        }
                        
                        print!("\r{}", result);
                        stdout().flush().unwrap();
                        thread::sleep(Duration::from_secs_f64(speed));
                    }
                }
                println!();
            }
            _ => {
                println!("Unknown animation type: {}", animation_type);
            }
        }
    }

    #[staticmethod]
    #[pyo3(signature = (data, headers=None, padding=1, border_style="single", fg_color=None, bg_color=None, style=None, header_color=None, cell_colors=None, align="left"))]
    fn table(
        data: Vec<Vec<String>>,
        headers: Option<Vec<String>>,
        padding: usize,
        border_style: &str,
        fg_color: Option<u8>,
        bg_color: Option<u8>,
        style: Option<u8>,
        header_color: Option<(u8, u8, u8)>,
        cell_colors: Option<Vec<Vec<Option<(u8, u8, u8)>>>>,
        align: &str,
    ) -> String {
        if data.is_empty() && headers.is_none() {
            return String::new();
        }

        let borders = get_border_chars(border_style);
        
        let mut all_rows = Vec::new();
        if let Some(h) = headers.as_ref() {
            all_rows.push(h.clone());
        }
        all_rows.extend(data.clone());
        
        if all_rows.is_empty() {
            return String::new();
        }
        
        let num_cols = all_rows[0].len();
        let mut col_widths = vec![0; num_cols];
        
        for row in &all_rows {
            for (i, cell) in row.iter().enumerate() {
                if i < col_widths.len() {
                    col_widths[i] = col_widths[i].max(cell.len());
                }
            }
        }
        
        let format_cell = |content: &str, width: usize, alignment: &str| -> String {
            match alignment {
                "right" => format!("{:>width$}", content, width = width),
                "center" => format!("{:^width$}", content, width = width),
                _ => format!("{:<width$}", content, width = width),
            }
        };
        
        let create_separator = |left: &str, mid: &str, right: &str, fill: &str| -> String {
            let parts: Vec<String> = col_widths
                .iter()
                .map(|w| fill.repeat(w + padding * 2))
                .collect();
            format!("{}{}{}", left, parts.join(mid), right)
        };
        
        let mut result = Vec::new();
        result.push(create_separator(&borders.tl, &borders.t, &borders.tr, &borders.t));
        
        let mut data_start_idx = 0;
        if let Some(h) = headers.as_ref() {
            let mut header_row = borders.l.to_string();
            for (header, width) in h.iter().zip(&col_widths) {
                let mut cell = format!(
                    "{}{}{}",
                    " ".repeat(padding),
                    format_cell(header, *width, align),
                    " ".repeat(padding)
                );
                
                if let Some((r, g, b)) = header_color {
                    cell = Self::rgb(&cell, r, g, b, None, None);
                }
                
                header_row.push_str(&cell);
                header_row.push_str(&borders.l);
            }
            result.push(header_row);
            result.push(create_separator(&borders.ml, &borders.m, &borders.mr, &borders.m));
            data_start_idx = 1;
        }
        
        for (row_idx, row) in all_rows[data_start_idx..].iter().enumerate() {
            let mut row_str = borders.l.to_string();
            for (col_idx, (cell, width)) in row.iter().zip(&col_widths).enumerate() {
                let mut cell_content = format!(
                    "{}{}{}",
                    " ".repeat(padding),
                    format_cell(cell, *width, align),
                    " ".repeat(padding)
                );
                
                if let Some(ref colors) = cell_colors {
                    if row_idx < colors.len() && col_idx < colors[row_idx].len() {
                        if let Some((r, g, b)) = colors[row_idx][col_idx] {
                            cell_content = Self::rgb(&cell_content, r, g, b, None, None);
                        }
                    }
                }
                
                row_str.push_str(&cell_content);
                row_str.push_str(&borders.l);
            }
            result.push(row_str);
        }
        
        result.push(create_separator(&borders.bl, &borders.b, &borders.br, &borders.b));
        
        let output = result.join("\n");
        
        if fg_color.is_some() || bg_color.is_some() || style.is_some() {
            Self::colorize(&output, fg_color, bg_color, style)
        } else {
            output
        }
    }

    #[staticmethod]
    #[pyo3(signature = (progress, width=50, fill_char="█", empty_char="░", start_char="|", end_char="|", show_percentage=true, bar_color=None, percentage_color=None))]
    fn progress_bar(
        progress: f64,
        width: usize,
        fill_char: &str,
        empty_char: &str,
        start_char: &str,
        end_char: &str,
        show_percentage: bool,
        bar_color: Option<(u8, u8, u8)>,
        percentage_color: Option<(u8, u8, u8)>,
    ) -> String {
        let progress = progress.max(0.0).min(1.0);
        let filled_width = (width as f64 * progress) as usize;
        let empty_width = width.saturating_sub(filled_width);
        
        let mut filled_part = fill_char.repeat(filled_width);
        let empty_part = empty_char.repeat(empty_width);
        
        if let Some((r, g, b)) = bar_color {
            filled_part = Self::rgb(&filled_part, r, g, b, None, None);
        }
        
        let mut bar = format!("{}{}{}{}", start_char, filled_part, empty_part, end_char);
        
        if show_percentage {
            let mut percentage = format!(" {}%", (progress * 100.0) as i32);
            if let Some((r, g, b)) = percentage_color {
                percentage = Self::rgb(&percentage, r, g, b, None, None);
            }
            bar.push_str(&percentage);
        }
        
        bar
    }

    #[staticmethod]
    fn multi_color_text(text: &str, color_map: HashMap<String, (u8, u8, u8)>) -> String {
        let mut result = text.to_string();
        
        for (substring, (r, g, b)) in color_map {
            if result.contains(&substring) {
                let colored = Self::rgb(&substring, r, g, b, None, None);
                result = result.replace(&substring, &colored);
            }
        }
        
        result
    }

    #[staticmethod]
    #[pyo3(signature = (text, pattern, fg_color=None, bg_color=None, style=None, case_sensitive=false))]
    fn highlight_text(
        text: &str,
        pattern: &str,
        fg_color: Option<u8>,
        bg_color: Option<u8>,
        style: Option<u8>,
        case_sensitive: bool,
    ) -> String {
        if pattern.is_empty() {
            return text.to_string();
        }
        
        let highlighted = Self::colorize(pattern, fg_color, bg_color, style);
        
        if case_sensitive {
            text.replace(pattern, &highlighted)
        } else {
            let lower_text = text.to_lowercase();
            let lower_pattern = pattern.to_lowercase();
            
            let mut result = String::new();
            let mut last_idx = 0;
            
            for (idx, _) in lower_text.match_indices(&lower_pattern) {
                result.push_str(&text[last_idx..idx]);
                let original = &text[idx..idx + pattern.len()];
                result.push_str(&Self::colorize(original, fg_color, bg_color, style));
                last_idx = idx + pattern.len();
            }
            result.push_str(&text[last_idx..]);
            
            result
        }
    }

    #[staticmethod]
    #[pyo3(signature = (text, speed=0.05, style=None, color=None))]
    fn typewriter_effect(text: &str, speed: f64, style: Option<u8>, color: Option<(u8, u8, u8)>) {
        for ch in text.chars() {
            let char_display = if let Some((r, g, b)) = color {
                Self::rgb(&ch.to_string(), r, g, b, None, style)
            } else if let Some(s) = style {
                Self::colorize(&ch.to_string(), None, None, Some(s))
            } else {
                ch.to_string()
            };
            
            print!("{}", char_display);
            stdout().flush().unwrap();
            thread::sleep(Duration::from_secs_f64(speed));
        }
        println!();
    }

    #[staticmethod]
    #[pyo3(signature = (text="Loading", duration=5.0, spinner_style="dots", color=None))]
    fn spinner(text: &str, duration: f64, spinner_style: &str, color: Option<(u8, u8, u8)>) {
        let spinners = get_spinner_frames();
        let frames = spinners.get(spinner_style).unwrap_or(&spinners["dots"]);
        
        let start = Instant::now();
        let mut idx = 0;
        
        while start.elapsed().as_secs_f64() < duration {
            let frame = &frames[idx % frames.len()];
            let colored_frame = if let Some((r, g, b)) = color {
                Self::rgb(frame, r, g, b, None, None)
            } else {
                frame.to_string()
            };
            
            print!("\r{} {}", colored_frame, text);
            stdout().flush().unwrap();
            thread::sleep(Duration::from_millis(100));
            idx += 1;
        }
        
        print!("\r{}\r", " ".repeat(text.len() + 10));
        stdout().flush().unwrap();
    }

    #[staticmethod]
    fn random_color(text: &str, style: Option<u8>) -> String {
        let mut rng = rand::thread_rng();
        let r = rng.gen::<u8>();
        let g = rng.gen::<u8>();
        let b = rng.gen::<u8>();
        
        Self::rgb(text, r, g, b, None, style)
    }

    #[staticmethod]
    fn random_bg(text: &str, style: Option<u8>) -> String {
        let mut rng = rand::thread_rng();
        let bg_r = rng.gen::<u8>();
        let bg_g = rng.gen::<u8>();
        let bg_b = rng.gen::<u8>();
        
        let luminance = (0.299 * bg_r as f64 + 0.587 * bg_g as f64 + 0.114 * bg_b as f64) / 255.0;
        let (fg_r, fg_g, fg_b) = if luminance > 0.5 {
            (0, 0, 0)
        } else {
            (255, 255, 255)
        };
        
        Self::rgb_bg(text, bg_r, bg_g, bg_b, Some(fg_r), Some(fg_g), Some(fg_b), style)
    }

    #[staticmethod]
    fn batch_colorize(texts: Vec<String>, r: u8, g: u8, b: u8) -> Vec<String> {
        texts
            .into_iter()
            .map(|text| Self::rgb(&text, r, g, b, None, None))
            .collect()
    }

    #[staticmethod]
    fn strip_ansi(text: &str) -> String {
        let re = regex::Regex::new(r"\x1b\[[0-9;]*m").unwrap();
        re.replace_all(text, "").to_string()
    }

    #[staticmethod]
    fn visible_length(text: &str) -> usize {
        Self::strip_ansi(text).chars().count()
    }

    #[staticmethod]
    #[pyo3(signature = (text, width, r, g, b, indent=0))]
    fn wrap_colored(
        text: &str,
        width: usize,
        r: u8,
        g: u8,
        b: u8,
        indent: usize,
    ) -> Vec<String> {
        let indent_str = " ".repeat(indent);
        let mut lines = Vec::new();
        let words: Vec<&str> = text.split_whitespace().collect();
        let mut current_line = String::new();
        
        for word in words {
            if current_line.len() + word.len() + 1 > width {
                if !current_line.is_empty() {
                    lines.push(format!("{}{}", indent_str, Self::rgb(&current_line.trim(), r, g, b, None, None)));
                    current_line.clear();
                }
            }
            current_line.push_str(word);
            current_line.push(' ');
        }
        
        if !current_line.is_empty() {
            lines.push(format!("{}{}", indent_str, Self::rgb(&current_line.trim(), r, g, b, None, None)));
        }
        
        lines
    }

    #[staticmethod]
    fn interpolate_colors(
        color1: (u8, u8, u8),
        color2: (u8, u8, u8),
        steps: usize,
    ) -> Vec<(u8, u8, u8)> {
        let mut colors = Vec::with_capacity(steps);
        
        for i in 0..steps {
            let ratio = i as f64 / (steps - 1).max(1) as f64;
            let r = (color1.0 as f64 + (color2.0 as i16 - color1.0 as i16) as f64 * ratio) as u8;
            let g = (color1.1 as f64 + (color2.1 as i16 - color1.1 as i16) as f64 * ratio) as u8;
            let b = (color1.2 as f64 + (color2.2 as i16 - color1.2 as i16) as f64 * ratio) as u8;
            colors.push((r, g, b));
        }
        
        colors
    }

    #[staticmethod]
    #[pyo3(signature = (palette_type="basic"))]
    fn show_palette(palette_type: &str) -> String {
        let mut result = String::new();
        
        match palette_type {
            "basic" => {
                result.push_str("Basic Colors:\n");
                for i in 30..38 {
                    result.push_str(&format!("{} ", Self::colorize("██", Some(i), None, None)));
                }
                result.push('\n');
            }
            "256" => {
                result.push_str("256 Color Palette:\n");
                for i in 0..=255 {
                    result.push_str(&Self::color256("█", i, None, None));
                    if (i + 1) % 16 == 0 {
                        result.push('\n');
                    }
                }
            }
            "rgb" => {
                result.push_str("RGB Spectrum Sample:\n");
                for r in (0..=255).step_by(51){
                    for g in (0..=255).step_by(51) {
                        for b in (0..=255).step_by(51) {
                            result.push_str(&Self::rgb("█", r, g, b, None, None));
                        }
                        result.push('\n');
                    }
                }
            }
            _ => {
                result = "Unknown palette type. Use 'basic', '256', or 'rgb'".to_string();
            }
        }
        
      result
    }

    #[staticmethod]
    #[pyo3(signature = (text, padding=1, border_style="single", fg_color=None, bg_color=None, style=None))]
    fn box_text(
        text: &str,
        padding: usize,
        border_style: &str,
        fg_color: Option<u8>,
        bg_color: Option<u8>,
        style: Option<u8>,
    ) -> String {
        let lines: Vec<&str> = text.lines().collect();
        let width = lines.iter().map(|l| l.chars().count()).max().unwrap_or(0);
        
        let borders = get_border_chars(border_style);
        
        let horizontal_border = format!(
            "{}{}{}",
            borders.tl,
            borders.t.repeat(width + padding * 2),
            borders.tr
        );
        let bottom_border = format!(
            "{}{}{}",
            borders.bl,
            borders.b.repeat(width + padding * 2),
            borders.br
        );
        let padding_line = format!(
            "{}{}{}",
            borders.l,
            " ".repeat(width + padding * 2),
            borders.r
        );
        
        let mut result = Vec::new();
        result.push(horizontal_border);
        
        for _ in 0..padding {
            result.push(padding_line.clone());
        }
        
        for line in lines {
            let char_count = line.chars().count();
            let padded_line = format!(
                "{}{}{}{}{}",
                borders.l,
                " ".repeat(padding),
                line,
                " ".repeat(width - char_count + padding),
                borders.r
            );
            result.push(padded_line);
        }
        
        for _ in 0..padding {
            result.push(padding_line.clone());
        }
        
        result.push(bottom_border);
        
        let output = result.join("\n");
        
        if fg_color.is_some() || bg_color.is_some() || style.is_some() {
            Self::colorize(&output, fg_color, bg_color, style)
        } else {
            output
        }
    }

    #[staticmethod]
    fn gradient_vertical(lines: Vec<String>, start_rgb: (u8, u8, u8), end_rgb: (u8, u8, u8)) -> String {
        if lines.is_empty() {
            return String::new();
        }
        
        let len = lines.len();
        let mut result = Vec::with_capacity(len);
        
        for (i, line) in lines.iter().enumerate() {
            let ratio = if len > 1 {
                i as f64 / (len - 1) as f64
            } else {
                0.0
            };
            
            let r = (start_rgb.0 as f64 + (end_rgb.0 as i16 - start_rgb.0 as i16) as f64 * ratio) as u8;
            let g = (start_rgb.1 as f64 + (end_rgb.1 as i16 - start_rgb.1 as i16) as f64 * ratio) as u8;
            let b = (start_rgb.2 as f64 + (end_rgb.2 as i16 - start_rgb.2 as i16) as f64 * ratio) as u8;
            
            result.push(Self::rgb(line, r, g, b, None, None));
        }
        
        result.join("\n")
    }

    #[staticmethod]
    #[pyo3(signature = (duration=5.0, columns=80, density=0.3))]
    fn matrix_rain(duration: f64, columns: usize, density: f64) {
        let chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789@#$%^&*()";
        let chars_vec: Vec<char> = chars.chars().collect();
        let mut rng = rand::thread_rng();
        
        let start = Instant::now();
        
        while start.elapsed().as_secs_f64() < duration {
            let mut line = String::new();
            
            for _ in 0..columns {
                if rng.gen::<f64>() < density {
                    let ch = chars_vec[rng.gen_range(0..chars_vec.len())];
                    let brightness = rng.gen_range(100..=255);
                    line.push_str(&Self::rgb(&ch.to_string(), 0, brightness, 0, None, None));
                } else {
                    line.push(' ');
                }
            }
            
            println!("{}", line);
            thread::sleep(Duration::from_millis(50));
        }
    }

    #[staticmethod]
    fn fire_text(text: &str) -> String {
        let mut result = String::new();
        let mut rng = rand::thread_rng();
        
        for ch in text.chars() {
            if ch.is_whitespace() {
                result.push(ch);
                continue;
            }
            
            let color_choice = rng.gen_range(0..3);
            let (r, g, b) = match color_choice {
                0 => (255, rng.gen_range(50..=100), 0),
                1 => (255, rng.gen_range(100..=200), 0),
                _ => (255, rng.gen_range(200..=255), 0),
            };
            
            result.push_str(&Self::rgb(&ch.to_string(), r, g, b, None, Some(BOLD)));
        }
        
        result
    }

    #[staticmethod]
    fn neon_glow(text: &str, color: (u8, u8, u8)) -> String {
        let (r, g, b) = color;
        let mut result = String::new();
        
        let dim1 = Self::rgb(text, r/3, g/3, b/3, None, None);
        let dim2 = Self::rgb(text, r/2, g/2, b/2, None, None);
        let bright = Self::rgb(text, r, g, b, None, Some(BOLD));
        
        result.push_str(&format!("{} {} {}", dim1, bright, dim2));
        result
    }

    #[staticmethod]
    fn pastel(text: &str) -> String {
        let mut result = String::new();
        let mut rng = rand::thread_rng();
        
        let pastel_colors = vec![
            (255, 179, 186),
            (255, 223, 186),
            (255, 255, 186),
            (186, 255, 201),
            (186, 225, 255),
            (218, 186, 255),
        ];
        
        for ch in text.chars() {
            if ch.is_whitespace() {
                result.push(ch);
                continue;
            }
            
            let (r, g, b) = pastel_colors[rng.gen_range(0..pastel_colors.len())];
            result.push_str(&Self::rgb(&ch.to_string(), r, g, b, None, None));
        }
        
        result
    }

    #[staticmethod]
    fn glitch_text(text: &str) -> String {
        let mut result = String::new();
        let mut rng = rand::thread_rng();
        
        for ch in text.chars() {
            if rng.gen::<f64>() < 0.1 {
                let glitch_colors = vec![
                    (255, 0, 255),
                    (0, 255, 255),
                    (255, 0, 0),
                ];
                let (r, g, b) = glitch_colors[rng.gen_range(0..glitch_colors.len())];
                result.push_str(&Self::rgb(&ch.to_string(), r, g, b, None, None));
            } else {
                result.push(ch);
            }
        }
        
        result
    }

    #[staticmethod]
    fn metallic(text: &str, metal_type: Option<&str>) -> String {
        let colors = match metal_type.unwrap_or("silver") {
            "gold" => vec![
                (255, 215, 0),
                (255, 235, 100),
                (255, 255, 150),
                (255, 235, 100),
                (255, 215, 0),
            ],
            "bronze" => vec![
                (205, 127, 50),
                (230, 150, 80),
                (240, 170, 100),
                (230, 150, 80),
                (205, 127, 50),
            ],
            "copper" => vec![
                (184, 115, 51),
                (220, 140, 70),
                (240, 160, 90),
                (220, 140, 70),
                (184, 115, 51),
            ],
            _ => vec![
                (192, 192, 192),
                (220, 220, 220),
                (255, 255, 255),
                (220, 220, 220),
                (192, 192, 192),
            ],
        };
        
        let mut result = String::new();
        let mut color_idx = 0;
        
        for ch in text.chars() {
            if ch.is_whitespace() {
                result.push(ch);
                continue;
            }
            
            let (r, g, b) = colors[color_idx % colors.len()];
            result.push_str(&Self::rgb(&ch.to_string(), r, g, b, None, Some(BOLD)));
            color_idx += 1;
        }
        
        result
    }

    #[staticmethod]
    #[pyo3(signature = (text, outline_color=(255, 255, 255), fill_color=(0, 0, 0)))]
    fn outline_text(text: &str, outline_color: (u8, u8, u8), fill_color: (u8, u8, u8)) -> Vec<String> {
        let mut lines = Vec::new();
        
        lines.push(Self::rgb(&format!(" {} ", text), outline_color.0, outline_color.1, outline_color.2, None, None));
        
        let middle = format!(
            "{}{}{}",
            Self::rgb(" ", outline_color.0, outline_color.1, outline_color.2, None, None),
            Self::rgb(text, fill_color.0, fill_color.1, fill_color.2, None, None),
            Self::rgb(" ", outline_color.0, outline_color.1, outline_color.2, None, None)
        );
        lines.push(middle);
        
        lines.push(Self::rgb(&format!(" {} ", text), outline_color.0, outline_color.1, outline_color.2, None, None));
        
        lines
    }

    #[staticmethod]
    #[pyo3(signature = (text, text_color=(255, 255, 255), shadow_color=(100, 100, 100), shadow_offset=2))]
    fn shadow_text(
        text: &str,
        text_color: (u8, u8, u8),
        shadow_color: (u8, u8, u8),
        shadow_offset: usize,
    ) -> String {
        let shadow = format!(
            "{}{}",
            " ".repeat(shadow_offset),
            Self::rgb(text, shadow_color.0, shadow_color.1, shadow_color.2, None, None)
        );
        let main_text = Self::rgb(text, text_color.0, text_color.1, text_color.2, None, Some(BOLD));
        
        format!("{}\n{}", shadow, main_text)
    }

    #[staticmethod]
    fn underwave(text: &str, color: (u8, u8, u8)) -> String {
        let wave = "∼".repeat(text.chars().count());
        let colored_text = Self::rgb(text, color.0, color.1, color.2, None, None);
        let colored_wave = Self::rgb(&wave, color.0, color.1, color.2, None, Some(DIM));
        
        format!("{}\n{}", colored_text, colored_wave)
    }

    #[staticmethod]
    fn temperature_tint(text: &str, temperature: f64) -> String {
        let temp = temperature.max(-1.0).min(1.0);
        
        let (r, g, b) = if temp >= 0.0 {
            (255, (255.0 * (1.0 - temp * 0.3)) as u8, (255.0 * (1.0 - temp * 0.7)) as u8)
        } else {
            ((255.0 * (1.0 + temp * 0.7)) as u8, (255.0 * (1.0 + temp * 0.3)) as u8, 255)
        };
        
        Self::rgb(text, r, g, b, None, None)
    }

    #[staticmethod]
    fn colorize_ascii_art(art: Vec<String>, gradient_start: (u8, u8, u8), gradient_end: (u8, u8, u8)) -> String {
        Self::gradient_vertical(art, gradient_start, gradient_end)
    }

    #[staticmethod]
    fn list_presets() -> Vec<String> {
        get_color_presets().keys().map(|s| s.to_string()).collect()
    }

    #[staticmethod]
    fn list_themes() -> Vec<String> {
        get_theme_presets().keys().map(|s| s.to_string()).collect()
    }

    #[staticmethod]
    fn rgb_to_hsl(r: u8, g: u8, b: u8) -> (f64, f64, f64) {
        let r = r as f64 / 255.0;
        let g = g as f64 / 255.0;
        let b = b as f64 / 255.0;
        
        let max = r.max(g).max(b);
        let min = r.min(g).min(b);
        let delta = max - min;
        
        let l = (max + min) / 2.0;
        
        if delta == 0.0 {
            return (0.0, 0.0, l);
        }
        
        let s = if l < 0.5 {
            delta / (max + min)
        } else {
            delta / (2.0 - max - min)
        };
        
        let h = if max == r {
            60.0 * (((g - b) / delta) % 6.0)
        } else if max == g {
            60.0 * (((b - r) / delta) + 2.0)
        } else {
            60.0 * (((r - g) / delta) + 4.0)
        };
        
        let h = if h < 0.0 { h + 360.0 } else { h };
        
        (h, s, l)
    }

    #[staticmethod]
    fn color_distance(color1: (u8, u8, u8), color2: (u8, u8, u8)) -> f64 {
        let dr = color1.0 as f64 - color2.0 as f64;
        let dg = color1.1 as f64 - color2.1 as f64;
        let db = color1.2 as f64 - color2.2 as f64;
        
        (dr * dr + dg * dg + db * db).sqrt()
    }

    #[staticmethod]
    fn closest_preset(r: u8, g: u8, b: u8) -> String {
        let presets = get_color_presets();
        let target = (r, g, b);
        
        let mut closest_name = String::new();
        let mut min_distance = f64::MAX;
        
        for (name, color) in presets.iter() {
            let distance = Self::color_distance(target, *color);
            if distance < min_distance {
                min_distance = distance;
                closest_name = name.clone();
            }
        }
        
        closest_name
    }

    #[staticmethod]
    fn complementary_color(r: u8, g: u8, b: u8) -> (u8, u8, u8) {
        let (h, s, l) = Self::rgb_to_hsl(r, g, b);
        let comp_h = (h + 180.0) % 360.0;
        Self::hsl_to_rgb(comp_h, s, l)
    }

    #[staticmethod]
    fn analogous_colors(r: u8, g: u8, b: u8, angle: Option<f64>) -> Vec<(u8, u8, u8)> {
        let angle = angle.unwrap_or(30.0);
        let (h, s, l) = Self::rgb_to_hsl(r, g, b);
        
        vec![
            Self::hsl_to_rgb((h - angle + 360.0) % 360.0, s, l),
            (r, g, b),
            Self::hsl_to_rgb((h + angle) % 360.0, s, l),
        ]
    }

    #[staticmethod]
    fn triadic_colors(r: u8, g: u8, b: u8) -> Vec<(u8, u8, u8)> {
        let (h, s, l) = Self::rgb_to_hsl(r, g, b);
        
        vec![
            (r, g, b),
            Self::hsl_to_rgb((h + 120.0) % 360.0, s, l),
            Self::hsl_to_rgb((h + 240.0) % 360.0, s, l),
        ]
    }

    #[staticmethod]
    fn lighten(r: u8, g: u8, b: u8, amount: f64) -> (u8, u8, u8) {
        let (h, s, l) = Self::rgb_to_hsl(r, g, b);
        let new_l = (l + amount).min(1.0);
        Self::hsl_to_rgb(h, s, new_l)
    }

    #[staticmethod]
    fn darken(r: u8, g: u8, b: u8, amount: f64) -> (u8, u8, u8) {
        let (h, s, l) = Self::rgb_to_hsl(r, g, b);
        let new_l = (l - amount).max(0.0);
        Self::hsl_to_rgb(h, s, new_l)
    }

    #[staticmethod]
    fn saturate(r: u8, g: u8, b: u8, amount: f64) -> (u8, u8, u8) {
        let (h, s, l) = Self::rgb_to_hsl(r, g, b);
        let new_s = (s + amount).min(1.0);
        Self::hsl_to_rgb(h, new_s, l)
    }

    #[staticmethod]
    fn desaturate(r: u8, g: u8, b: u8, amount: f64) -> (u8, u8, u8) {
        let (h, s, l) = Self::rgb_to_hsl(r, g, b);
        let new_s = (s - amount).max(0.0);
        Self::hsl_to_rgb(h, new_s, l)
    }

    #[staticmethod]
    fn invert_color(r: u8, g: u8, b: u8) -> (u8, u8, u8) {
        (255 - r, 255 - g, 255 - b)
    }

    #[staticmethod]
    fn grayscale(text: &str, r: u8, g: u8, b: u8) -> String {
        let gray = (0.299 * r as f64 + 0.587 * g as f64 + 0.114 * b as f64) as u8;
        Self::rgb(text, gray, gray, gray, None, None)
    }

    #[staticmethod]
    fn sepia(text: &str, r: u8, g: u8, b: u8) -> String {
        let tr = ((r as f64 * 0.393) + (g as f64 * 0.769) + (b as f64 * 0.189)).min(255.0) as u8;
        let tg = ((r as f64 * 0.349) + (g as f64 * 0.686) + (b as f64 * 0.168)).min(255.0) as u8;
        let tb = ((r as f64 * 0.272) + (g as f64 * 0.534) + (b as f64 * 0.131)).min(255.0) as u8;
        Self::rgb(text, tr, tg, tb, None, None)
    }

    #[staticmethod]
    fn blend_colors(color1: (u8, u8, u8), color2: (u8, u8, u8), ratio: f64) -> (u8, u8, u8) {
        let ratio = ratio.max(0.0).min(1.0);
        let r = (color1.0 as f64 * (1.0 - ratio) + color2.0 as f64 * ratio) as u8;
        let g = (color1.1 as f64 * (1.0 - ratio) + color2.1 as f64 * ratio) as u8;
        let b = (color1.2 as f64 * (1.0 - ratio) + color2.2 as f64 * ratio) as u8;
        (r, g, b)
    }

    #[staticmethod]
    fn pulse_frames(text: &str, color: (u8, u8, u8), steps: usize) -> Vec<String> {
        let (h, s, l) = Self::rgb_to_hsl(color.0, color.1, color.2);
        let mut frames = Vec::new();
        
        for i in 0..steps {
            let brightness = l + (i as f64 / steps as f64) * (1.0 - l);
            let (r, g, b) = Self::hsl_to_rgb(h, s, brightness);
            frames.push(Self::rgb(text, r, g, b, None, Some(BOLD)));
        }
        
        for i in (0..steps).rev() {
            let brightness = l + (i as f64 / steps as f64) * (1.0 - l);
            let (r, g, b) = Self::hsl_to_rgb(h, s, brightness);
            frames.push(Self::rgb(text, r, g, b, None, Some(BOLD)));
        }
        
        frames
    }

    #[staticmethod]
    fn wave_frames(text: &str, color: (u8, u8, u8), wave_length: usize) -> Vec<String> {
        let mut frames = Vec::new();
        
        for offset in 0..wave_length {
            let mut result = String::new();
            for (i, ch) in text.chars().enumerate() {
                let amplitude = ((i + offset) as f64 * std::f64::consts::PI / wave_length as f64).sin();
                let brightness = 0.5 + amplitude * 0.5;
                
                let r = (color.0 as f64 * brightness) as u8;
                let g = (color.1 as f64 * brightness) as u8;
                let b = (color.2 as f64 * brightness) as u8;
                
                result.push_str(&Self::rgb(&ch.to_string(), r, g, b, None, None));
            }
            frames.push(result);
        }
        
        frames
    }

    #[staticmethod]
    fn generate_palette(base_color: (u8, u8, u8), scheme: &str) -> PyResult<Vec<(u8, u8, u8)>> {
        let (r, g, b) = base_color;
        
        match scheme {
            "monochromatic" => {
                let (h, s, l) = Self::rgb_to_hsl(r, g, b);
                Ok(vec![
                    Self::hsl_to_rgb(h, s, l * 0.3),
                    Self::hsl_to_rgb(h, s, l * 0.5),
                    Self::hsl_to_rgb(h, s, l * 0.7),
                    base_color,
                    Self::hsl_to_rgb(h, s, (l * 1.2).min(1.0)),
                ])
            }
            "analogous" => Ok(Self::analogous_colors(r, g, b, None)),
            "complementary" => {
                let comp = Self::complementary_color(r, g, b);
                Ok(vec![base_color, comp])
            }
            "triadic" => Ok(Self::triadic_colors(r, g, b)),
            "split_complementary" => {
                let (h, s, l) = Self::rgb_to_hsl(r, g, b);
                Ok(vec![
                    base_color,
                    Self::hsl_to_rgb((h + 150.0) % 360.0, s, l),
                    Self::hsl_to_rgb((h + 210.0) % 360.0, s, l),
                ])
            }
            "tetradic" => {
                let (h, s, l) = Self::rgb_to_hsl(r, g, b);
                Ok(vec![
                    base_color,
                    Self::hsl_to_rgb((h + 90.0) % 360.0, s, l),
                    Self::hsl_to_rgb((h + 180.0) % 360.0, s, l),
                    Self::hsl_to_rgb((h + 270.0) % 360.0, s, l),
                ])
            }
            _ => Err(PyValueError::new_err(
                "Unknown scheme. Use: monochromatic, analogous, complementary, triadic, split_complementary, or tetradic"
            ))
        }
    }

    #[staticmethod]
    fn color_swatch(colors: Vec<(u8, u8, u8)>, width: Option<usize>) -> String {
        let width = width.unwrap_or(5);
        let block = "█".repeat(width);
        
        let mut result = String::new();
        for (r, g, b) in colors {
            result.push_str(&Self::rgb(&block, r, g, b, None, None));
            result.push_str(&format!(" RGB({}, {}, {})\n", r, g, b));
        }
        
        result
    }

    #[staticmethod]
    #[pyo3(signature = (title, content, width=60, color=(100, 150, 255)))]
    fn panel(title: &str, content: Vec<String>, width: usize, color: (u8, u8, u8)) -> String {
        let borders = get_border_chars("rounded");
        let title_len = title.chars().count();
        let title_padding = (width.saturating_sub(title_len + 2)) / 2;
        
        let mut result = Vec::new();
        
        let top = format!(
            "{}{}[ {} ]{}{}",
            borders.tl,
            borders.t.repeat(title_padding),
            Self::rgb(title, color.0, color.1, color.2, None, Some(BOLD)),
            borders.t.repeat(width.saturating_sub(title_padding + title_len + 4)),
            borders.tr
        );
        result.push(top);
        
        for line in content {
            let line_len = Self::visible_length(&line);
            let padding = width.saturating_sub(line_len + 2);
            result.push(format!("{} {}{} {}", borders.l, line, " ".repeat(padding), borders.r));
        }
        
        result.push(format!("{}{}{}", borders.bl, borders.b.repeat(width), borders.br));
        
        result.join("\n")
    }

    #[staticmethod]
    fn badge(label: &str, value: &str, style: Option<&str>) -> String {
        let (label_bg, label_fg, value_bg, value_fg) = match style.unwrap_or("default") {
            "success" => ((0, 128, 0), (255, 255, 255), (0, 200, 0), (255, 255, 255)),
            "error" => ((128, 0, 0), (255, 255, 255), (200, 0, 0), (255, 255, 255)),
            "warning" => ((200, 150, 0), (0, 0, 0), (255, 200, 0), (0, 0, 0)),
            "info" => ((0, 100, 200), (255, 255, 255), (0, 150, 255), (255, 255, 255)),
            _ => ((80, 80, 80), (255, 255, 255), (120, 120, 120), (255, 255, 255)),
        };
        
        let label_part = Self::rgb_bg(&format!(" {} ", label), label_bg.0, label_bg.1, label_bg.2,
                                       Some(label_fg.0), Some(label_fg.1), Some(label_fg.2), Some(BOLD));
        let value_part = Self::rgb_bg(&format!(" {} ", value), value_bg.0, value_bg.1, value_bg.2,
                                       Some(value_fg.0), Some(value_fg.1), Some(value_fg.2), None);
        
        format!("{}{}", label_part, value_part)
    }

    #[staticmethod]
    #[pyo3(signature = (width=80, char="─", color=None, label=None))]
    fn divider(width: usize, char: &str, color: Option<(u8, u8, u8)>, label: Option<&str>) -> String {
        if let Some(text) = label {
            let text_len = text.chars().count();
            let left_width = (width.saturating_sub(text_len + 2)) / 2;
            let right_width = width.saturating_sub(left_width + text_len + 2);
            
            let left = char.repeat(left_width);
            let right = char.repeat(right_width);
            
            if let Some((r, g, b)) = color {
                format!("{} {} {}", 
                    Self::rgb(&left, r, g, b, None, None),
                    Self::rgb(text, r, g, b, None, Some(BOLD)),
                    Self::rgb(&right, r, g, b, None, None)
                )
            } else {
                format!("{} {} {}", left, text, right)
            }
        } else {
            let line = char.repeat(width);
            if let Some((r, g, b)) = color {
                Self::rgb(&line, r, g, b, None, None)
            } else {
                line
            }
        }
    }

    #[staticmethod]
    #[pyo3(signature = (items, bullet="•", color=None, indent=2))]
    fn bullet_list(items: Vec<String>, bullet: &str, color: Option<(u8, u8, u8)>, indent: usize) -> String {
      let indent_str = " ".repeat(indent);
        let mut result = Vec::new();
        
        for item in items {
            let colored_bullet = if let Some((r, g, b)) = color {
                Self::rgb(bullet, r, g, b, None, Some(BOLD))
            } else {
                bullet.to_string()
            };
            
            result.push(format!("{}{} {}", indent_str, colored_bullet, item));
        }
        
        result.join("\n")
    }

    #[staticmethod]
    #[pyo3(signature = (items, color=None, indent=2))]
    fn numbered_list(items: Vec<String>, color: Option<(u8, u8, u8)>, indent: usize) -> String {
        let indent_str = " ".repeat(indent);
        let mut result = Vec::new();
        
        for (i, item) in items.iter().enumerate() {
            let number = format!("{}.", i + 1);
            let colored_number = if let Some((r, g, b)) = color {
                Self::rgb(&number, r, g, b, None, Some(BOLD))
            } else {
                number
            };
            
            result.push(format!("{}{} {}", indent_str, colored_number, item));
        }
        
        result.join("\n")
    }

    #[staticmethod]
    #[pyo3(signature = (total_steps=100, desc="Loading", bar_color=(0, 255, 0), width=50))]
    fn loading_bar_demo(total_steps: usize, desc: &str, bar_color: (u8, u8, u8), width: usize) {
        for i in 0..=total_steps {
            let progress = i as f64 / total_steps as f64;
            let bar = Self::progress_bar(
                progress,
                width,
                "█",
                "░",
                "|",
                "|",
                true,
                Some(bar_color),
                Some((255, 255, 0))
            );
            
            print!("\r{} {}", desc, bar);
            stdout().flush().unwrap();
            thread::sleep(Duration::from_millis(20));
        }
        println!();
    }

    #[staticmethod]
    fn format_bytes(bytes: u64) -> String {
        const UNITS: &[&str] = &["B", "KB", "MB", "GB", "TB"];
    let mut size = bytes as f64;
        let mut unit_idx = 0;
        
        while size >= 1024.0 && unit_idx < UNITS.len() - 1 {
            size /= 1024.0;
            unit_idx += 1;
        }
        
        let (r, g, b) = match unit_idx {
            0 => (150, 150, 150),
            1 => (100, 200, 100),
            2 => (100, 150, 255),
            3 => (255, 150, 0),
            _ => (255, 100, 100),
        };
        
        let formatted = format!("{:.2} {}", size, UNITS[unit_idx]);
        Self::rgb(&formatted, r, g, b, None, Some(BOLD))
    }

    #[staticmethod]
    fn format_duration(seconds: f64) -> String {
        let (value, unit, color) = if seconds < 1.0 {
            (seconds * 1000.0, "ms", (100, 200, 100))
        } else if seconds < 60.0 {
            (seconds, "s", (100, 150, 255))
        } else if seconds < 3600.0 {
            (seconds / 60.0, "m", (255, 200, 100))
        } else {
            (seconds / 3600.0, "h", (255, 150, 150))
        };
        
        let formatted = format!("{:.2}{}", value, unit);
        Self::rgb(&formatted, color.0, color.1, color.2, None, Some(BOLD))
    }

    #[staticmethod]
    fn diff_line(line: &str, line_type: &str) -> String {
        match line_type {
            "added" | "+" => Self::rgb(&format!("+{}", line), 0, 255, 0, None, None),
            "removed" | "-" => Self::rgb(&format!("-{}", line), 255, 0, 0, None, None),
            "context" | " " => format!(" {}", line),
            "info" | "@" => Self::rgb(&format!("@{}", line), 0, 200, 255, None, Some(BOLD)),
            _ => line.to_string(),
        }
    }

    #[staticmethod]
    fn log_level(level: &str, message: &str) -> String {
        let (label, color) = match level.to_uppercase().as_str() {
            "ERROR" | "FATAL" => ("ERROR", (255, 0, 0)),
            "WARN" | "WARNING" => ("WARN ", (255, 200, 0)),
            "INFO" => ("INFO ", (0, 200, 255)),
            "DEBUG" => ("DEBUG", (150, 150, 150)),
            "TRACE" => ("TRACE", (200, 200, 200)),
            "SUCCESS" | "OK" => ("OK   ", (0, 255, 0)),
            _ => (level, (255, 255, 255)),
        };
        
        let colored_label = Self::rgb_bg(
            &format!(" {} ", label),
            color.0, color.1, color.2,
            Some(0), Some(0), Some(0),
            Some(BOLD)
        );
        
        format!("{} {}", colored_label, message)
    }
}

// Helper structures and functions
struct BorderChars {
    tl: String,
    t: String,
    tr: String,
    l: String,
    r: String,
    ml: String,
    m: String,
    mr: String,
    bl: String,
    b: String,
    br: String,
}

fn get_border_chars(style: &str) -> BorderChars {
    match style {
        "double" => BorderChars {
            tl: "╔".to_string(),
            t: "═".to_string(),
            tr: "╗".to_string(),
            l: "║".to_string(),
            r: "║".to_string(),
            ml: "╠".to_string(),
            m: "═".to_string(),
            mr: "╣".to_string(),
            bl: "╚".to_string(),
            b: "═".to_string(),
            br: "╝".to_string(),
        },
        "rounded" => BorderChars {
            tl: "╭".to_string(),
            t: "─".to_string(),
            tr: "╮".to_string(),
            l: "│".to_string(),
            r: "│".to_string(),
            ml: "├".to_string(),
            m: "─".to_string(),
            mr: "┤".to_string(),
            bl: "╰".to_string(),
            b: "─".to_string(),
            br: "╯".to_string(),
        },
        "bold" => BorderChars {
    tl: "┏".to_string(),
            t: "━".to_string(),
            tr: "┓".to_string(),
            l: "┃".to_string(),
            r: "┃".to_string(),
            ml: "┣".to_string(),
            m: "━".to_string(),
            mr: "┫".to_string(),
            bl: "┗".to_string(),
            b: "━".to_string(),
            br: "┛".to_string(),
        },
        "dashed" => BorderChars {
            tl: "┌".to_string(),
            t: "┄".to_string(),
            tr: "┐".to_string(),
            l: "┆".to_string(),
            r: "┆".to_string(),
            ml: "├".to_string(),
            m: "┄".to_string(),
            mr: "┤".to_string(),
            bl: "└".to_string(),
            b: "┄".to_string(),
            br: "┘".to_string(),
        },
        _ => BorderChars {
            tl: "┌".to_string(),
            t: "─".to_string(),
            tr: "┐".to_string(),
            l: "│".to_string(),
            r: "│".to_string(),
            ml: "├".to_string(),
            m: "─".to_string(),
            mr: "┤".to_string(),
            bl: "└".to_string(),
            b: "─".to_string(),
            br: "┘".to_string(),
        },
    }
}

struct Theme {
    fg: (u8, u8, u8),
    bg: (u8, u8, u8),
    style: Option<u8>,
}

fn get_theme_presets() -> HashMap<String, Theme> {
    let mut themes = HashMap::new();
    
    themes.insert("matrix".to_string(), Theme {
        fg: (0, 255, 0),
        bg: (0, 0, 0),
        style: Some(BOLD),
    });
    
    themes.insert("mehvish".to_string(), Theme {
        fg: (0, 191, 255),
        bg: (0, 0, 139),
        style: None,
    });
    
    themes.insert("sunset".to_string(), Theme {
        fg: (255, 165, 0),
        bg: (178, 34, 34),
        style: None,
    });
    
    themes.insert("forest".to_string(), Theme {
        fg: (34, 139, 34),
        bg: (0, 100, 0),
        style: None,
    });
    
    themes.insert("neon".to_string(), Theme {
        fg: (255, 0, 255),
        bg: (0, 0, 0),
        style: Some(BOLD),
    });
    
    themes.insert("pastel".to_string(), Theme {
        fg: (255, 192, 203),
        bg: (230, 230, 250),
        style: None,
    });
    
    themes.insert("retro".to_string(), Theme {
        fg: (255, 165, 0),
        bg: (0, 0, 0),
        style: Some(BOLD),
    });
    
    themes.insert("cyberpunk".to_string(), Theme {
        fg: (0, 255, 255),
        bg: (139, 0, 139),
        style: Some(BOLD),
    });
    
    themes.insert("desert".to_string(), Theme {
        fg: (210, 180, 140),
        bg: (244, 164, 96),
        style: None,
    });
    
    themes.insert("dracula".to_string(), Theme {
        fg: (248, 248, 242),
        bg: (40, 42, 54),
        style: None,
    });
    
    themes
}

fn get_color_presets() -> HashMap<String, (u8, u8, u8)> {
    let mut presets = HashMap::new();
    
    presets.insert("forest_green".to_string(), (34, 139, 34));
    presets.insert("sky_blue".to_string(), (135, 206, 235));
    presets.insert("coral".to_string(), (255, 127, 80));
    presets.insert("gold".to_string(), (255, 215, 0));
    presets.insert("lavender".to_string(), (230, 230, 250));
    presets.insert("tomato".to_string(), (255, 99, 71));
    presets.insert("teal".to_string(), (0, 128, 128));
    presets.insert("salmon".to_string(), (250, 128, 114));
    presets.insert("violet".to_string(), (238, 130, 238));
    presets.insert("khaki".to_string(), (240, 230, 140));
    presets.insert("turquoise".to_string(), (64, 224, 208));
    presets.insert("firebrick".to_string(), (178, 34, 34));
    presets.insert("navy".to_string(), (0, 0, 128));
    presets.insert("steel_blue".to_string(), (70, 130, 180));
    presets.insert("olive".to_string(), (128, 128, 0));
    presets.insert("spring_green".to_string(), (0, 255, 127));
    presets.insert("crimson".to_string(), (220, 20, 60));
    presets.insert("chocolate".to_string(), (210, 105, 30));
    presets.insert("midnight_blue".to_string(), (25, 25, 112));
    presets.insert("orchid".to_string(), (218, 112, 214));
    
    presets
}

fn get_spinner_frames() -> HashMap<String, Vec<String>> {
    let mut spinners = HashMap::new();
    
    spinners.insert("dots".to_string(), vec![
        "⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"
    ].into_iter().map(|s| s.to_string()).collect());
    
    spinners.insert("line".to_string(), vec![
        "|", "/", "-", "\\"
    ].into_iter().map(|s| s.to_string()).collect());
    
    spinners.insert("arrow".to_string(), vec![
        "←", "↖", "↑", "↗", "→", "↘", "↓", "↙"
    ].into_iter().map(|s| s.to_string()).collect());
    
    spinners.insert("circle".to_string(), vec![
        "◐", "◓", "◑", "◒"
    ].into_iter().map(|s| s.to_string()).collect());
    
    spinners.insert("box".to_string(), vec![
        "◰", "◳", "◲", "◱"
    ].into_iter().map(|s| s.to_string()).collect());
    
    spinners.insert("bounce".to_string(), vec![
        "⠁", "⠂", "⠄", "⠂"
    ].into_iter().map(|s| s.to_string()).collect());
    
    spinners
}

#[pymodule]
fn chromin(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<ColoredText>()?;
    
    m.add("BLACK", BLACK)?;
    m.add("RED", RED)?;
    m.add("GREEN", GREEN)?;
    m.add("YELLOW", YELLOW)?;
    m.add("BLUE", BLUE)?;
    m.add("MAGENTA", MAGENTA)?;
    m.add("CYAN", CYAN)?;
    m.add("WHITE", WHITE)?;
    
    m.add("BRIGHT_BLACK", BRIGHT_BLACK)?;
    m.add("BRIGHT_RED", BRIGHT_RED)?;
    m.add("BRIGHT_GREEN", BRIGHT_GREEN)?;
    m.add("BRIGHT_YELLOW", BRIGHT_YELLOW)?;
    m.add("BRIGHT_BLUE", BRIGHT_BLUE)?;
    m.add("BRIGHT_MAGENTA", BRIGHT_MAGENTA)?;
    m.add("BRIGHT_CYAN", BRIGHT_CYAN)?;
    m.add("BRIGHT_WHITE", BRIGHT_WHITE)?;
    
    m.add("BG_BLACK", BG_BLACK)?;
    m.add("BG_RED", BG_RED)?;
    m.add("BG_GREEN", BG_GREEN)?;
    m.add("BG_YELLOW", BG_YELLOW)?;
    m.add("BG_BLUE", BG_BLUE)?;
    m.add("BG_MAGENTA", BG_MAGENTA)?;
    m.add("BG_CYAN", BG_CYAN)?;
    m.add("BG_WHITE", BG_WHITE)?;
    
    m.add("BG_BRIGHT_BLACK", BG_BRIGHT_BLACK)?;
    m.add("BG_BRIGHT_RED", BG_BRIGHT_RED)?;
    m.add("BG_BRIGHT_GREEN", BG_BRIGHT_GREEN)?;
    m.add("BG_BRIGHT_YELLOW", BG_BRIGHT_YELLOW)?;
    m.add("BG_BRIGHT_BLUE", BG_BRIGHT_BLUE)?;
    m.add("BG_BRIGHT_MAGENTA", BG_BRIGHT_MAGENTA)?;
    m.add("BG_BRIGHT_CYAN", BG_BRIGHT_CYAN)?;
    m.add("BG_BRIGHT_WHITE", BG_BRIGHT_WHITE)?;
    
    m.add("BOLD", BOLD)?;
    m.add("DIM", DIM)?;
    m.add("ITALIC", ITALIC)?;
    m.add("UNDERLINE", UNDERLINE)?;
    m.add("BLINK", BLINK)?;
    m.add("RAPID_BLINK", RAPID_BLINK)?;
    m.add("REVERSE", REVERSE)?;
    m.add("HIDDEN", HIDDEN)?;
    m.add("STRIKETHROUGH", STRIKETHROUGH)?;
    m.add("RESET", RESET)?;
    
    Ok(())
}
