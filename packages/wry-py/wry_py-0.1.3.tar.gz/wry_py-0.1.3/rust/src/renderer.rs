use crate::elements::ElementDef;

/// Render an ElementDef tree to HTML string
pub fn render_to_html(element: &ElementDef) -> String {
    render_element(element)
}

fn render_element(el: &ElementDef) -> String {
    match el.element_type.as_str() {
        "text" => render_text(el),
        "button" => render_button(el),
        "image" => render_image(el),
        "input" => render_input(el),
        _ => render_div(el), // div is default
    }
}

fn render_div(el: &ElementDef) -> String {
    let mut classes = Vec::new();
    let mut styles = Vec::new();

    // Layout classes
    if el.size_full {
        classes.push("size-full");
    }

    match el.flex_direction.as_deref() {
        Some("column") => classes.push("flex-col"),
        Some("row") => classes.push("flex-row"),
        _ => {}
    }

    match el.align_items.as_deref() {
        Some("center") => classes.push("items-center"),
        Some("start") | Some("flex-start") => classes.push("items-start"),
        Some("end") | Some("flex-end") => classes.push("items-end"),
        _ => {}
    }

    match el.justify_content.as_deref() {
        Some("center") => classes.push("justify-center"),
        Some("space-between") => classes.push("justify-between"),
        Some("start") | Some("flex-start") => classes.push("justify-start"),
        Some("end") | Some("flex-end") => classes.push("justify-end"),
        _ => {}
    }

    // Inline styles
    if let Some(w) = el.width {
        styles.push(format!("width: {}px", w));
    }
    if let Some(h) = el.height {
        styles.push(format!("height: {}px", h));
    }
    if let Some(g) = el.gap {
        styles.push(format!("gap: {}px", g));
    }
    if let Some(p) = el.padding {
        styles.push(format!("padding: {}px", p));
    }
    if let Some(pt) = el.padding_top {
        styles.push(format!("padding-top: {}px", pt));
    }
    if let Some(pr) = el.padding_right {
        styles.push(format!("padding-right: {}px", pr));
    }
    if let Some(pb) = el.padding_bottom {
        styles.push(format!("padding-bottom: {}px", pb));
    }
    if let Some(pl) = el.padding_left {
        styles.push(format!("padding-left: {}px", pl));
    }
    if let Some(m) = el.margin {
        styles.push(format!("margin: {}px", m));
    }
    if let Some(ref bg) = el.background_color {
        styles.push(format!("background-color: {}", bg));
    }
    if let Some(ref tc) = el.text_color {
        styles.push(format!("color: {}", tc));
    }
    if let Some(br) = el.border_radius {
        styles.push(format!("border-radius: {}px", br));
    }
    if let Some(bw) = el.border_width {
        let bc = el.border_color.as_deref().unwrap_or("#333");
        styles.push(format!("border: {}px solid {}", bw, bc));
    }
    if let Some(ref overflow) = el.overflow {
        styles.push(format!("overflow: {}", overflow));
    }
    if let Some(ref text_align) = el.text_align {
        styles.push(format!("text-align: {}", text_align));
    }
    if let Some(ref word_wrap) = el.word_wrap {
        styles.push(format!("word-wrap: {}", word_wrap));
    }
    if let Some(ref position) = el.position {
        styles.push(format!("position: {}", position));
    }
    if let Some(top) = el.top {
        styles.push(format!("top: {}px", top));
    }
    if let Some(right) = el.right {
        styles.push(format!("right: {}px", right));
    }
    if let Some(bottom) = el.bottom {
        styles.push(format!("bottom: {}px", bottom));
    }
    if let Some(left) = el.left {
        styles.push(format!("left: {}px", left));
    }
    if let Some(fs) = el.font_size {
        styles.push(format!("font-size: {}px", fs));
    }
    if let Some(ref fw) = el.font_weight {
        styles.push(format!("font-weight: {}", fw));
    }

    // Build attributes
    let class_attr = if classes.is_empty() {
        String::new()
    } else {
        format!(" class=\"{}\"", classes.join(" "))
    };

    let style_attr = if styles.is_empty() {
        String::new()
    } else {
        format!(" style=\"{}\"", styles.join("; "))
    };

    let onclick_attr = if let Some(ref cb_id) = el.on_click {
        format!(" onclick=\"handleClick('{}')\"", escape_html(cb_id))
    } else {
        String::new()
    };

    // Render children
    let children_html: String = el.children.iter().map(render_element).collect();

    // Text content (if any)
    let text_content = el.text_content.as_ref().map(|t| escape_html(t)).unwrap_or_default();

    format!(
        "<div id=\"{}\"{}{}{}>{}{}</div>",
        escape_html(&el.id),
        class_attr,
        style_attr,
        onclick_attr,
        text_content,
        children_html
    )
}

fn render_text(el: &ElementDef) -> String {
    let mut styles = Vec::new();

    if let Some(ref tc) = el.text_color {
        styles.push(format!("color: {}", tc));
    }
    if let Some(fs) = el.font_size {
        styles.push(format!("font-size: {}px", fs));
    }
    if let Some(ref fw) = el.font_weight {
        styles.push(format!("font-weight: {}", fw));
    }
    if let Some(ref text_align) = el.text_align {
        styles.push(format!("text-align: {}", text_align));
    }
    if let Some(ref word_wrap) = el.word_wrap {
        styles.push(format!("word-wrap: {}", word_wrap));
    }
    if let Some(p) = el.padding {
        styles.push(format!("padding: {}px", p));
    }

    let style_attr = if styles.is_empty() {
        String::new()
    } else {
        format!(" style=\"{}\"", styles.join("; "))
    };

    let text = el.text_content.as_ref().map(|t| escape_html(t)).unwrap_or_default();

    format!("<span id=\"{}\"{}>{}</span>", escape_html(&el.id), style_attr, text)
}

fn render_button(el: &ElementDef) -> String {
    let mut styles = vec![
        "cursor: pointer".to_string(),
        "padding: 8px 16px".to_string(),
        "border: none".to_string(),
        "border-radius: 6px".to_string(),
        "background: #3b82f6".to_string(),
        "color: white".to_string(),
        "font-size: 14px".to_string(),
    ];

    if let Some(ref bg) = el.background_color {
        styles.retain(|s| !s.starts_with("background:"));
        styles.push(format!("background: {}", bg));
    }
    if let Some(ref tc) = el.text_color {
        styles.retain(|s| !s.starts_with("color:"));
        styles.push(format!("color: {}", tc));
    }
    if let Some(br) = el.border_radius {
        styles.retain(|s| !s.starts_with("border-radius:"));
        styles.push(format!("border-radius: {}px", br));
    }
    if let Some(fs) = el.font_size {
        styles.retain(|s| !s.starts_with("font-size:"));
        styles.push(format!("font-size: {}px", fs));
    }
    if let Some(p) = el.padding {
        styles.retain(|s| !s.starts_with("padding:"));
        styles.push(format!("padding: {}px", p));
    }

    let style_attr = format!(" style=\"{}\"", styles.join("; "));

    let onclick_attr = if let Some(ref cb_id) = el.on_click {
        format!(" onclick=\"handleClick('{}')\"", escape_html(cb_id))
    } else {
        String::new()
    };

    let text = el.text_content.as_ref().map(|t| escape_html(t)).unwrap_or_default();

    format!(
        "<button id=\"{}\"{}{}>{}</button>",
        escape_html(&el.id),
        style_attr,
        onclick_attr,
        text
    )
}

fn render_image(el: &ElementDef) -> String {
    let mut styles = Vec::new();

    if let Some(w) = el.width {
        styles.push(format!("width: {}px", w));
    }
    if let Some(h) = el.height {
        styles.push(format!("height: {}px", h));
    }
    if let Some(br) = el.border_radius {
        styles.push(format!("border-radius: {}px", br));
    }

    let style_attr = if styles.is_empty() {
        String::new()
    } else {
        format!(" style=\"{}\"", styles.join("; "))
    };

    let src = el.text_content.as_ref().map(|t| escape_html(t)).unwrap_or_default();

    format!(
        "<img id=\"{}\" src=\"{}\"{} />",
        escape_html(&el.id),
        src,
        style_attr
    )
}

fn render_input(el: &ElementDef) -> String {
    let mut styles = vec![
        "padding: 8px 12px".to_string(),
        "border: 1px solid #555".to_string(),
        "border-radius: 4px".to_string(),
        "background: #2a2a3a".to_string(),
        "color: white".to_string(),
        "font-size: 14px".to_string(),
        "outline: none".to_string(),
    ];

    if let Some(w) = el.width {
        styles.push(format!("width: {}px", w));
    }
    if let Some(h) = el.height {
        styles.push(format!("height: {}px", h));
    }
    if let Some(ref bg) = el.background_color {
        styles.retain(|s| !s.starts_with("background:"));
        styles.push(format!("background: {}", bg));
    }
    if let Some(ref tc) = el.text_color {
        styles.retain(|s| !s.starts_with("color:"));
        styles.push(format!("color: {}", tc));
    }
    if let Some(br) = el.border_radius {
        styles.retain(|s| !s.starts_with("border-radius:"));
        styles.push(format!("border-radius: {}px", br));
    }
    if let Some(p) = el.padding {
        styles.retain(|s| !s.starts_with("padding:"));
        styles.push(format!("padding: {}px", p));
    }

    let style_attr = format!(" style=\"{}\"", styles.join("; "));

    let oninput_attr = if let Some(ref cb_id) = el.on_input {
        format!(" oninput=\"handleInput('{}', this.value)\"", escape_html(cb_id))
    } else {
        String::new()
    };

    let value_attr = el.value.as_ref()
        .map(|v| format!(" value=\"{}\"", escape_html(v)))
        .unwrap_or_default();

    let placeholder_attr = el.placeholder.as_ref()
        .map(|p| format!(" placeholder=\"{}\"", escape_html(p)))
        .unwrap_or_default();

    format!(
        "<input id=\"{}\" type=\"text\"{}{}{}{}/>",
        escape_html(&el.id),
        style_attr,
        oninput_attr,
        value_attr,
        placeholder_attr
    )
}

fn escape_html(s: &str) -> String {
    s.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
        .replace('\'', "&#39;")
}
