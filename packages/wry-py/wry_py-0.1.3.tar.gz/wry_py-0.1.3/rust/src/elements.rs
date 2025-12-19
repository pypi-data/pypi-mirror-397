use pyo3::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Mutex;

/// Serializable element definition sent to frontend.
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ElementDef {
    pub id: String,
    pub element_type: String,

    // Layout
    #[serde(skip_serializing_if = "Option::is_none")]
    pub width: Option<f32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub height: Option<f32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub flex_direction: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub align_items: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub justify_content: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub gap: Option<f32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub padding: Option<f32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub padding_top: Option<f32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub padding_right: Option<f32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub padding_bottom: Option<f32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub padding_left: Option<f32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub margin: Option<f32>,
    pub size_full: bool,

    // Styling
    #[serde(skip_serializing_if = "Option::is_none")]
    pub background_color: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub text_color: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub border_radius: Option<f32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub border_width: Option<f32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub border_color: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub overflow: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub text_align: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub word_wrap: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub position: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub top: Option<f32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub right: Option<f32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub bottom: Option<f32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub left: Option<f32>,

    // Text
    #[serde(skip_serializing_if = "Option::is_none")]
    pub text_content: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub font_size: Option<f32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub font_weight: Option<String>,

    // Interactivity
    #[serde(skip_serializing_if = "Option::is_none")]
    pub on_click: Option<String>, // callback ID
    #[serde(skip_serializing_if = "Option::is_none")]
    pub on_input: Option<String>, // callback ID for input changes
    #[serde(skip_serializing_if = "Option::is_none")]
    pub value: Option<String>, // input value
    #[serde(skip_serializing_if = "Option::is_none")]
    pub placeholder: Option<String>,

    // Children
    #[serde(default)]
    pub children: Vec<ElementDef>,
}

impl Default for ElementDef {
    fn default() -> Self {
        Self {
            id: uuid(),
            element_type: "div".to_string(),
            width: None,
            height: None,
            flex_direction: None,
            align_items: None,
            justify_content: None,
            gap: None,
            padding: None,
            padding_top: None,
            padding_right: None,
            padding_bottom: None,
            padding_left: None,
            margin: None,
            size_full: false,
            background_color: None,
            text_color: None,
            border_radius: None,
            border_width: None,
            border_color: None,
            overflow: None,
            text_align: None,
            word_wrap: None,
            position: None,
            top: None,
            right: None,
            bottom: None,
            left: None,
            text_content: None,
            font_size: None,
            font_weight: None,
            on_click: None,
            on_input: None,
            value: None,
            placeholder: None,
            children: Vec::new(),
        }
    }
}

fn uuid() -> String {
    use std::time::{SystemTime, UNIX_EPOCH};
    static COUNTER: std::sync::atomic::AtomicU64 = std::sync::atomic::AtomicU64::new(0);
    let count = COUNTER.fetch_add(1, std::sync::atomic::Ordering::SeqCst);
    let nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_nanos();
    format!("el_{:x}_{}", nanos, count)
}

// Global callback store
static CALLBACK_STORE: Mutex<Option<HashMap<String, Py<PyAny>>>> = Mutex::new(None);

fn init_callback_store() {
    let mut store = CALLBACK_STORE.lock().unwrap();
    if store.is_none() {
        *store = Some(HashMap::new());
    }
}

fn store_callback(id: String, callback: Py<PyAny>) {
    init_callback_store();
    let mut store = CALLBACK_STORE.lock().unwrap();
    if let Some(ref mut map) = *store {
        map.insert(id, callback);
    }
}

pub fn take_callbacks() -> HashMap<String, Py<PyAny>> {
    init_callback_store();
    let mut store = CALLBACK_STORE.lock().unwrap();
    store.take().unwrap_or_default()
}

/// Python Element class
#[pyclass]
#[derive(Clone)]
pub struct Element {
    pub def: ElementDef,
    callback_ids: Vec<String>,
}

#[pymethods]
impl Element {
    /// Create a new element.
    ///
    /// Args:
    ///     element_type: The HTML element type (e.g., "div", "button"). Defaults to "div".
    #[new]
    #[pyo3(text_signature = "(element_type=None)")]
    fn new(element_type: Option<String>) -> Self {
        let mut def = ElementDef::default();
        if let Some(t) = element_type {
            def.element_type = t;
        }
        Element {
            def,
            callback_ids: Vec::new(),
        }
    }

    /// Convert the element to a JSON string.
    ///
    /// Returns:
    ///     JSON representation of the element and all its properties.
    #[pyo3(text_signature = "($self)")]
    fn to_json(&self) -> PyResult<String> {
        serde_json::to_string(&self.def)
            .map_err(|e| pyo3::exceptions::PyValueError::new_err(e.to_string()))
    }

    fn __repr__(&self) -> String {
        format!(
            "Element(type='{}', children={})",
            self.def.element_type,
            self.def.children.len()
        )
    }
}

impl Element {
    pub fn collect_callbacks(&self) -> HashMap<String, Py<PyAny>> {
        take_callbacks()
    }
}

/// Builder pattern for creating elements
#[pyclass]
#[derive(Clone)]
pub struct ElementBuilder {
    element: Element,
}

#[pymethods]
impl ElementBuilder {
    /// Create a div element (generic container).
    #[staticmethod]
    #[pyo3(text_signature = "()")]
    fn div() -> Self {
        ElementBuilder {
            element: Element::new(Some("div".to_string())),
        }
    }

    /// Create a text element.
    ///
    /// Args:
    ///     content: The text to display.
    #[staticmethod]
    #[pyo3(text_signature = "(content)")]
    fn text(content: String) -> Self {
        let mut element = Element::new(Some("text".to_string()));
        element.def.text_content = Some(content);
        ElementBuilder { element }
    }

    /// Create a button element.
    ///
    /// Args:
    ///     label: The text to display on the button.
    #[staticmethod]
    #[pyo3(text_signature = "(label)")]
    fn button(label: String) -> Self {
        let mut element = Element::new(Some("button".to_string()));
        element.def.text_content = Some(label);
        ElementBuilder { element }
    }

    /// Create an image element.
    ///
    /// Args:
    ///     src: The image source URL or path.
    #[staticmethod]
    #[pyo3(text_signature = "(src)")]
    fn image(src: String) -> Self {
        let mut element = Element::new(Some("image".to_string()));
        element.def.text_content = Some(src);
        ElementBuilder { element }
    }

    /// Create an input field element.
    #[staticmethod]
    #[pyo3(text_signature = "()")]
    fn input() -> Self {
        ElementBuilder {
            element: Element::new(Some("input".to_string())),
        }
    }

    /// Set width in pixels. Returns self for chaining.
    #[pyo3(text_signature = "($self, w)")]
    fn width(mut slf: PyRefMut<'_, Self>, w: f32) -> PyRefMut<'_, Self> {
        slf.element.def.width = Some(w);
        slf
    }

    /// Set height in pixels. Returns self for chaining.
    #[pyo3(text_signature = "($self, h)")]
    fn height(mut slf: PyRefMut<'_, Self>, h: f32) -> PyRefMut<'_, Self> {
        slf.element.def.height = Some(h);
        slf
    }

    /// Set both width and height in pixels. Returns self for chaining.
    #[pyo3(text_signature = "($self, w, h)")]
    fn size(mut slf: PyRefMut<'_, Self>, w: f32, h: f32) -> PyRefMut<'_, Self> {
        slf.element.def.width = Some(w);
        slf.element.def.height = Some(h);
        slf
    }

    /// Make element fill available space
    #[pyo3(text_signature = "($self)")]
    fn size_full(mut slf: PyRefMut<'_, Self>) -> PyRefMut<'_, Self> {
        slf.element.def.size_full = true;
        slf
    }

    /// Use vertical (column) flex layout. Returns self for chaining.
    #[pyo3(text_signature = "($self)")]
    fn v_flex(mut slf: PyRefMut<'_, Self>) -> PyRefMut<'_, Self> {
        slf.element.def.flex_direction = Some("column".to_string());
        slf
    }

    /// Use horizontal (row) flex layout. Returns self for chaining.
    #[pyo3(text_signature = "($self)")]
    fn h_flex(mut slf: PyRefMut<'_, Self>) -> PyRefMut<'_, Self> {
        slf.element.def.flex_direction = Some("row".to_string());
        slf
    }

    /// Center child items perpendicular to flex direction. Returns self for chaining.
    #[pyo3(text_signature = "($self)")]
    fn items_center(mut slf: PyRefMut<'_, Self>) -> PyRefMut<'_, Self> {
        slf.element.def.align_items = Some("center".to_string());
        slf
    }

    /// Center content along the flex direction. Returns self for chaining.
    #[pyo3(text_signature = "($self)")]
    fn justify_center(mut slf: PyRefMut<'_, Self>) -> PyRefMut<'_, Self> {
        slf.element.def.justify_content = Some("center".to_string());
        slf
    }

    /// Distribute children evenly with space between them. Returns self for chaining.
    #[pyo3(text_signature = "($self)")]
    fn justify_between(mut slf: PyRefMut<'_, Self>) -> PyRefMut<'_, Self> {
        slf.element.def.justify_content = Some("space-between".to_string());
        slf
    }

    /// Set spacing between child elements in pixels. Returns self for chaining.
    #[pyo3(text_signature = "($self, g)")]
    fn gap(mut slf: PyRefMut<'_, Self>, g: f32) -> PyRefMut<'_, Self> {
        slf.element.def.gap = Some(g);
        slf
    }

    /// Set padding in pixels. With one arg, applies to all sides. With two args, (vertical, horizontal).
    #[pyo3(signature = (y, x = None), text_signature = "($self, y, x=None)")]
    fn padding(mut slf: PyRefMut<'_, Self>, y: f32, x: Option<f32>) -> PyRefMut<'_, Self> {
        match x {
            Some(h) => {
                slf.element.def.padding_top = Some(y);
                slf.element.def.padding_bottom = Some(y);
                slf.element.def.padding_left = Some(h);
                slf.element.def.padding_right = Some(h);
            }
            None => {
                slf.element.def.padding = Some(y);
            }
        }
        slf
    }

    /// Alias for padding
    #[pyo3(signature = (y, x = None), text_signature = "($self, y, x=None)")]
    fn p(mut slf: PyRefMut<'_, Self>, y: f32, x: Option<f32>) -> PyRefMut<'_, Self> {
        match x {
            Some(h) => {
                slf.element.def.padding_top = Some(y);
                slf.element.def.padding_bottom = Some(y);
                slf.element.def.padding_left = Some(h);
                slf.element.def.padding_right = Some(h);
            }
            None => {
                slf.element.def.padding = Some(y);
            }
        }
        slf
    }

    /// Set padding top
    #[pyo3(text_signature = "($self, p)")]
    fn pt(mut slf: PyRefMut<'_, Self>, p: f32) -> PyRefMut<'_, Self> {
        slf.element.def.padding_top = Some(p);
        slf
    }

    /// Set padding right
    #[pyo3(text_signature = "($self, p)")]
    fn pr(mut slf: PyRefMut<'_, Self>, p: f32) -> PyRefMut<'_, Self> {
        slf.element.def.padding_right = Some(p);
        slf
    }

    /// Set padding bottom
    #[pyo3(text_signature = "($self, p)")]
    fn pb(mut slf: PyRefMut<'_, Self>, p: f32) -> PyRefMut<'_, Self> {
        slf.element.def.padding_bottom = Some(p);
        slf
    }

    /// Set padding left
    #[pyo3(text_signature = "($self, p)")]
    fn pl(mut slf: PyRefMut<'_, Self>, p: f32) -> PyRefMut<'_, Self> {
        slf.element.def.padding_left = Some(p);
        slf
    }

    /// Set padding x (left and right)
    #[pyo3(text_signature = "($self, p)")]
    fn px(mut slf: PyRefMut<'_, Self>, p: f32) -> PyRefMut<'_, Self> {
        slf.element.def.padding_left = Some(p);
        slf.element.def.padding_right = Some(p);
        slf
    }

    /// Set padding y (top and bottom)
    #[pyo3(text_signature = "($self, p)")]
    fn py(mut slf: PyRefMut<'_, Self>, p: f32) -> PyRefMut<'_, Self> {
        slf.element.def.padding_top = Some(p);
        slf.element.def.padding_bottom = Some(p);
        slf
    }

    /// Set margin on all sides in pixels. Returns self for chaining.
    #[pyo3(text_signature = "($self, m)")]
    fn margin(mut slf: PyRefMut<'_, Self>, m: f32) -> PyRefMut<'_, Self> {
        slf.element.def.margin = Some(m);
        slf
    }

    /// Alias for margin
    #[pyo3(text_signature = "($self, m)")]
    fn m(mut slf: PyRefMut<'_, Self>, m: f32) -> PyRefMut<'_, Self> {
        slf.element.def.margin = Some(m);
        slf
    }

    /// Set background color. Accepts hex strings like "#ff0000" or CSS colors like "rgb(255,0,0)". Returns self for chaining.
    #[pyo3(text_signature = "($self, color)")]
    fn bg(mut slf: PyRefMut<'_, Self>, color: String) -> PyRefMut<'_, Self> {
        slf.element.def.background_color = Some(color);
        slf
    }

    /// Set text color. Returns self for chaining.
    #[pyo3(text_signature = "($self, color)")]
    fn text_color(mut slf: PyRefMut<'_, Self>, color: String) -> PyRefMut<'_, Self> {
        slf.element.def.text_color = Some(color);
        slf
    }

    /// Set border radius (rounded corners)
    #[pyo3(text_signature = "($self, radius)")]
    fn rounded(mut slf: PyRefMut<'_, Self>, radius: f32) -> PyRefMut<'_, Self> {
        slf.element.def.border_radius = Some(radius);
        slf
    }

    /// Set border with width and color. Returns self for chaining.
    #[pyo3(text_signature = "($self, width, color)")]
    fn border(mut slf: PyRefMut<'_, Self>, width: f32, color: String) -> PyRefMut<'_, Self> {
        slf.element.def.border_width = Some(width);
        slf.element.def.border_color = Some(color);
        slf
    }

    /// Short alias for border (1px solid color)
    #[pyo3(text_signature = "($self, color)")]
    fn b(mut slf: PyRefMut<'_, Self>, color: String) -> PyRefMut<'_, Self> {
        slf.element.def.border_width = Some(1.0);
        slf.element.def.border_color = Some(color);
        slf
    }

    /// Set overflow to hidden
    #[pyo3(text_signature = "($self)")]
    fn overflow_hidden(mut slf: PyRefMut<'_, Self>) -> PyRefMut<'_, Self> {
        slf.element.def.overflow = Some("hidden".to_string());
        slf
    }

    /// Set overflow
    #[pyo3(text_signature = "($self, value)")]
    fn overflow(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.element.def.overflow = Some(value);
        slf
    }

    /// Set text alignment
    #[pyo3(text_signature = "($self, align)")]
    fn text_align(mut slf: PyRefMut<'_, Self>, align: String) -> PyRefMut<'_, Self> {
        slf.element.def.text_align = Some(align);
        slf
    }

    /// Center text
    #[pyo3(text_signature = "($self)")]
    fn text_center(mut slf: PyRefMut<'_, Self>) -> PyRefMut<'_, Self> {
        slf.element.def.text_align = Some("center".to_string());
        slf
    }

    /// Set word wrap
    #[pyo3(text_signature = "($self, value)")]
    fn word_wrap(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.element.def.word_wrap = Some(value);
        slf
    }

    /// Set position
    #[pyo3(text_signature = "($self, value)")]
    fn position(mut slf: PyRefMut<'_, Self>, value: String) -> PyRefMut<'_, Self> {
        slf.element.def.position = Some(value);
        slf
    }

    /// Set position to absolute
    #[pyo3(text_signature = "($self)")]
    fn absolute(mut slf: PyRefMut<'_, Self>) -> PyRefMut<'_, Self> {
        slf.element.def.position = Some("absolute".to_string());
        slf
    }

    /// Set position to relative
    #[pyo3(text_signature = "($self)")]
    fn relative(mut slf: PyRefMut<'_, Self>) -> PyRefMut<'_, Self> {
        slf.element.def.position = Some("relative".to_string());
        slf
    }

    /// Set top position
    #[pyo3(text_signature = "($self, value)")]
    fn top(mut slf: PyRefMut<'_, Self>, value: f32) -> PyRefMut<'_, Self> {
        slf.element.def.top = Some(value);
        slf
    }

    /// Set right position
    #[pyo3(text_signature = "($self, value)")]
    fn right(mut slf: PyRefMut<'_, Self>, value: f32) -> PyRefMut<'_, Self> {
        slf.element.def.right = Some(value);
        slf
    }

    /// Set bottom position
    #[pyo3(text_signature = "($self, value)")]
    fn bottom(mut slf: PyRefMut<'_, Self>, value: f32) -> PyRefMut<'_, Self> {
        slf.element.def.bottom = Some(value);
        slf
    }

    /// Set left position
    #[pyo3(text_signature = "($self, value)")]
    fn left(mut slf: PyRefMut<'_, Self>, value: f32) -> PyRefMut<'_, Self> {
        slf.element.def.left = Some(value);
        slf
    }

    /// Set font size
    #[pyo3(text_signature = "($self, size)")]
    fn text_size(mut slf: PyRefMut<'_, Self>, size: f32) -> PyRefMut<'_, Self> {
        slf.element.def.font_size = Some(size);
        slf
    }

    /// Set font weight ("normal", "bold", "100"-"900")
    #[pyo3(text_signature = "($self, weight)")]
    fn text_weight(mut slf: PyRefMut<'_, Self>, weight: String) -> PyRefMut<'_, Self> {
        slf.element.def.font_weight = Some(weight);
        slf
    }

    /// Add a child element
    #[pyo3(text_signature = "($self, child)")]
    fn child(&mut self, child: &Element) -> Self {
        self.element.def.children.push(child.def.clone());
        self.element.callback_ids.extend(child.callback_ids.clone());
        self.clone()
    }

    /// Add a child from a builder
    #[pyo3(text_signature = "($self, child)")]
    fn child_builder(&mut self, child: &ElementBuilder) -> Self {
        self.element.def.children.push(child.element.def.clone());
        self.element.callback_ids.extend(child.element.callback_ids.clone());
        self.clone()
    }

    /// Add text child (convenience)
    #[pyo3(text_signature = "($self, text)")]
    fn child_text(mut slf: PyRefMut<'_, Self>, text: String) -> PyRefMut<'_, Self> {
        let mut text_def = ElementDef::default();
        text_def.element_type = "text".to_string();
        text_def.text_content = Some(text);
        slf.element.def.children.push(text_def);
        slf
    }

    /// Register a callback function to run when the element is clicked. Returns self for chaining.
    #[pyo3(text_signature = "($self, callback)")]
    fn on_click(&mut self, callback: Py<PyAny>) -> Self {
        let callback_id = uuid();
        self.element.def.on_click = Some(callback_id.clone());
        self.element.callback_ids.push(callback_id.clone());
        store_callback(callback_id, callback);
        self.clone()
    }

    /// Set input value
    #[pyo3(text_signature = "($self, val)")]
    fn value(mut slf: PyRefMut<'_, Self>, val: String) -> PyRefMut<'_, Self> {
        slf.element.def.value = Some(val);
        slf
    }

    /// Set placeholder text
    #[pyo3(text_signature = "($self, text)")]
    fn placeholder(mut slf: PyRefMut<'_, Self>, text: String) -> PyRefMut<'_, Self> {
        slf.element.def.placeholder = Some(text);
        slf
    }

    /// Register a callback function to run when the input value changes. Callback receives the new value as a string argument. Returns self for chaining.
    #[pyo3(text_signature = "($self, callback)")]
    fn on_input(&mut self, callback: Py<PyAny>) -> Self {
        let callback_id = uuid();
        self.element.def.on_input = Some(callback_id.clone());
        self.element.callback_ids.push(callback_id.clone());
        store_callback(callback_id, callback);
        self.clone()
    }

    /// Build and return the final Element. Call this after configuring all properties.
    #[pyo3(text_signature = "($self)")]
    fn build(&self) -> Element {
        self.element.clone()
    }

    fn __repr__(&self) -> String {
        format!("ElementBuilder({})", self.element.__repr__())
    }
}

// Convenience functions at module level for quick element creation.
/// Create a div element (generic container). Shorthand for ElementBuilder.div().
#[pyfunction]
#[pyo3(text_signature = "()")]
pub fn div() -> ElementBuilder {
    ElementBuilder::div()
}

/// Create a text element. Shorthand for ElementBuilder.text(content).
#[pyfunction]
#[pyo3(text_signature = "(content)")]
pub fn text(content: String) -> ElementBuilder {
    ElementBuilder::text(content)
}

/// Create a button element. Shorthand for ElementBuilder.button(label).
#[pyfunction]
#[pyo3(text_signature = "(label)")]
pub fn button(label: String) -> ElementBuilder {
    ElementBuilder::button(label)
}

/// Create an input field element. Shorthand for ElementBuilder.input().
#[pyfunction]
#[pyo3(text_signature = "()")]
pub fn input() -> ElementBuilder {
    ElementBuilder::input()
}
