use crate::elements::ElementDef;

/// Render an ElementDef tree to HTML string
pub fn render_to_html(element: &ElementDef) -> String {
    render_element(element)
}

/// Build hover/focus CSS styles for an element
fn build_state_styles(el: &ElementDef) -> String {
    let mut css = String::new();
    let id = escape_html(&el.id);

    // Hover styles
    let mut hover_styles = Vec::new();
    if let Some(ref bg) = el.hover_bg {
        hover_styles.push(format!("background-color: {} !important", bg));
    }
    if let Some(ref color) = el.hover_text_color {
        hover_styles.push(format!("color: {} !important", color));
    }
    if let Some(ref bc) = el.hover_border_color {
        hover_styles.push(format!("border-color: {} !important", bc));
    }
    if let Some(opacity) = el.hover_opacity {
        hover_styles.push(format!("opacity: {} !important", opacity));
    }
    if let Some(scale) = el.hover_scale {
        hover_styles.push(format!("transform: scale({}) !important", scale));
    }
    if !hover_styles.is_empty() {
        css.push_str(&format!("#{}:hover {{ {} }}", id, hover_styles.join("; ")));
    }

    // Focus styles
    let mut focus_styles = Vec::new();
    if let Some(ref bg) = el.focus_bg {
        focus_styles.push(format!("background-color: {} !important", bg));
    }
    if let Some(ref color) = el.focus_text_color {
        focus_styles.push(format!("color: {} !important", color));
    }
    if let Some(ref bc) = el.focus_border_color {
        focus_styles.push(format!("border-color: {} !important", bc));
    }
    if !focus_styles.is_empty() {
        css.push_str(&format!("#{}:focus {{ {} }}", id, focus_styles.join("; ")));
    }

    if css.is_empty() {
        String::new()
    } else {
        format!("<style>{}</style>", css)
    }
}

/// Build event handler attributes for an element
fn build_event_attrs(el: &ElementDef) -> String {
    let mut attrs = String::new();

    if let Some(ref cb_id) = el.on_click {
        attrs.push_str(&format!(" onclick=\"handleClick('{}')\"", escape_html(cb_id)));
    }
    if let Some(ref cb_id) = el.on_mouse_enter {
        attrs.push_str(&format!(" onmouseenter=\"handleMouseEvent('{}', 'mouse_enter')\"", escape_html(cb_id)));
    }
    if let Some(ref cb_id) = el.on_mouse_leave {
        attrs.push_str(&format!(" onmouseleave=\"handleMouseEvent('{}', 'mouse_leave')\"", escape_html(cb_id)));
    }
    if let Some(ref cb_id) = el.on_mouse_down {
        attrs.push_str(&format!(" onmousedown=\"handleMouseEvent('{}', 'mouse_down')\"", escape_html(cb_id)));
    }
    if let Some(ref cb_id) = el.on_mouse_up {
        attrs.push_str(&format!(" onmouseup=\"handleMouseEvent('{}', 'mouse_up')\"", escape_html(cb_id)));
    }

    attrs
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
    if let Some(ref transition) = el.transition {
        styles.push(format!("transition: {}", transition));
    }
    if let Some(opacity) = el.opacity {
        styles.push(format!("opacity: {}", opacity));
    }
    if let Some(ref cursor) = el.cursor {
        styles.push(format!("cursor: {}", cursor));
    }

    // Append any raw CSS provided via ElementDef.style
    if let Some(ref raw) = el.style {
        styles.push(escape_html(raw));
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

    let event_attrs = build_event_attrs(el);
    let state_styles = build_state_styles(el);

    // Render children
    let children_html: String = el.children.iter().map(render_element).collect();

    // Text content (if any)
    let text_content = el.text_content.as_ref().map(|t| escape_html(t)).unwrap_or_default();

    format!(
        "{}<div id=\"{}\"{}{}{}>{}{}</div>",
        state_styles,
        escape_html(&el.id),
        class_attr,
        style_attr,
        event_attrs,
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

    let event_attrs = build_event_attrs(el);
    let state_styles = build_state_styles(el);
    let text = el.text_content.as_ref().map(|t| escape_html(t)).unwrap_or_default();

    format!("{}<span id=\"{}\"{}{}>{}</span>", state_styles, escape_html(&el.id), style_attr, event_attrs, text)
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

    // Append any raw CSS provided via ElementDef.style
    if let Some(ref raw) = el.style {
        styles.push(escape_html(raw));
    }

    // Append any raw CSS provided via ElementDef.style
    if let Some(ref raw) = el.style {
        styles.push(escape_html(raw));
    }

    let style_attr = format!(" style=\"{}\"", styles.join("; "));
    let event_attrs = build_event_attrs(el);
    let state_styles = build_state_styles(el);
    let text = el.text_content.as_ref().map(|t| escape_html(t)).unwrap_or_default();

    format!(
        "{}<button id=\"{}\"{}{}>{}</button>",
        state_styles,
        escape_html(&el.id),
        style_attr,
        event_attrs,
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
    if let Some(ref of) = el.object_fit {
        styles.push(format!("object-fit: {}", of));
    }
    if let Some(ref transition) = el.transition {
        styles.push(format!("transition: {}", transition));
    }
    if let Some(opacity) = el.opacity {
        styles.push(format!("opacity: {}", opacity));
    }
    if let Some(ref cursor) = el.cursor {
        styles.push(format!("cursor: {}", cursor));
    }

    let style_attr = if styles.is_empty() {
        String::new()
    } else {
        format!(" style=\"{}\"", styles.join("; "))
    };

    let event_attrs = build_event_attrs(el);
    let state_styles = build_state_styles(el);
    let src = el.text_content.as_ref().map(|t| escape_html(t)).unwrap_or_default();
    let alt_attr = el.alt.as_ref()
        .map(|a| format!(" alt=\"{}\"", escape_html(a)))
        .unwrap_or_default();

    format!(
        "{}<img id=\"{}\" src=\"{}\"{}{}{}/>",
        state_styles,
        escape_html(&el.id),
        src,
        alt_attr,
        style_attr,
        event_attrs
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

    let event_attrs = build_event_attrs(el);
    let state_styles = build_state_styles(el);

    let value_attr = el.value.as_ref()
        .map(|v| format!(" value=\"{}\"", escape_html(v)))
        .unwrap_or_default();

    let placeholder_attr = el.placeholder.as_ref()
        .map(|p| format!(" placeholder=\"{}\"", escape_html(p)))
        .unwrap_or_default();

    format!(
        "{}<input id=\"{}\" type=\"text\"{}{}{}{}{}/>",
        state_styles,
        escape_html(&el.id),
        style_attr,
        oninput_attr,
        event_attrs,
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
