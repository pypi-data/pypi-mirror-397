/**
 * Chedito - Rich Text Editor for Django
 * Main initialization script
 */

(function() {
    'use strict';

    // Chedito namespace
    window.Chedito = window.Chedito || {};

    // Store all editor instances
    Chedito.editors = {};

    // Default configuration
    Chedito.defaults = {
        theme: 'snow',
        modules: {
            toolbar: [
                [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
                ['bold', 'italic', 'underline', 'strike'],
                [{ 'color': [] }, { 'background': [] }],
                [{ 'script': 'sub' }, { 'script': 'super' }],
                ['blockquote', 'code-block'],
                [{ 'list': 'ordered' }, { 'list': 'bullet' }],
                [{ 'indent': '-1' }, { 'indent': '+1' }],
                [{ 'direction': 'rtl' }],
                [{ 'align': [] }],
                ['link', 'image', 'video'],
                ['clean']
            ],
            clipboard: {
                matchVisual: false
            }
        },
        placeholder: 'Write something...'
    };

    // Accessibility labels for toolbar buttons
    Chedito.accessibilityLabels = {
        // Format buttons
        'bold': 'Bold',
        'italic': 'Italic',
        'underline': 'Underline',
        'strike': 'Strikethrough',

        // Script buttons
        'script[value="sub"]': 'Subscript',
        'script[value="super"]': 'Superscript',

        // Block buttons
        'blockquote': 'Block Quote',
        'code-block': 'Code Block',

        // List buttons
        'list[value="ordered"]': 'Numbered List',
        'list[value="bullet"]': 'Bulleted List',

        // Indent buttons
        'indent[value="-1"]': 'Decrease Indent',
        'indent[value="+1"]': 'Increase Indent',

        // Direction
        'direction[value="rtl"]': 'Right to Left Text Direction',

        // Align buttons
        'align[value=""]': 'Align Left',
        'align[value="center"]': 'Align Center',
        'align[value="right"]': 'Align Right',
        'align[value="justify"]': 'Justify',

        // Media buttons
        'link': 'Insert Link',
        'image': 'Insert Image',
        'video': 'Insert Video',

        // Clean button
        'clean': 'Remove Formatting',

        // Color pickers
        'color': 'Text Color',
        'background': 'Background Color',

        // Header dropdown
        'header': 'Heading Style',

        // Font and size
        'font': 'Font Family',
        'size': 'Font Size'
    };

    /**
     * Add accessibility attributes to toolbar buttons
     */
    Chedito.enhanceAccessibility = function(container) {
        const toolbar = container.querySelector('.ql-toolbar');
        if (!toolbar) return;

        // Set toolbar role
        toolbar.setAttribute('role', 'toolbar');
        toolbar.setAttribute('aria-label', 'Text Formatting Toolbar');

        // Get all buttons in the toolbar
        const buttons = toolbar.querySelectorAll('button');
        buttons.forEach(function(button) {
            // Determine the button type from its class
            let label = null;
            let buttonType = null;

            // Check for format classes
            const classList = button.className.split(' ');
            for (let cls of classList) {
                if (cls.startsWith('ql-')) {
                    buttonType = cls.substring(3); // Remove 'ql-' prefix
                    break;
                }
            }

            if (buttonType) {
                // Check if button has a value attribute
                const value = button.getAttribute('value');
                if (value !== null && value !== '') {
                    // Try to find label with value
                    const keyWithValue = buttonType + '[value="' + value + '"]';
                    label = Chedito.accessibilityLabels[keyWithValue];
                }

                // Fall back to base button type
                if (!label) {
                    label = Chedito.accessibilityLabels[buttonType];
                }

                // Generate a sensible label if not found
                if (!label) {
                    // Convert camelCase/kebab-case to readable text
                    label = buttonType
                        .replace(/-/g, ' ')
                        .replace(/([A-Z])/g, ' $1')
                        .replace(/^\w/, function(c) { return c.toUpperCase(); })
                        .trim();
                }

                // Set aria-label and title
                button.setAttribute('aria-label', label);
                button.setAttribute('title', label);

                // Ensure button has proper role
                if (!button.getAttribute('role')) {
                    button.setAttribute('role', 'button');
                }

                // Add aria-pressed for toggle buttons
                const toggleButtons = ['bold', 'italic', 'underline', 'strike', 'blockquote', 'code-block'];
                if (toggleButtons.includes(buttonType)) {
                    const isActive = button.classList.contains('ql-active');
                    button.setAttribute('aria-pressed', isActive ? 'true' : 'false');
                }
            }
        });

        // Handle select/picker elements (dropdowns)
        const pickers = toolbar.querySelectorAll('.ql-picker');
        pickers.forEach(function(picker) {
            let pickerType = null;
            const classList = picker.className.split(' ');
            for (let cls of classList) {
                if (cls.startsWith('ql-') && cls !== 'ql-picker' && !cls.startsWith('ql-expanded')) {
                    pickerType = cls.substring(3);
                    break;
                }
            }

            if (pickerType) {
                const label = Chedito.accessibilityLabels[pickerType] ||
                    pickerType.charAt(0).toUpperCase() + pickerType.slice(1);

                // Label the picker container
                picker.setAttribute('aria-label', label);

                // Find and label the picker label (the visible button part)
                const pickerLabel = picker.querySelector('.ql-picker-label');
                if (pickerLabel) {
                    pickerLabel.setAttribute('aria-label', label + ' dropdown');
                    pickerLabel.setAttribute('title', label);
                    pickerLabel.setAttribute('role', 'button');
                    pickerLabel.setAttribute('aria-haspopup', 'listbox');
                    pickerLabel.setAttribute('aria-expanded', 'false');
                }

                // Label the dropdown options
                const pickerOptions = picker.querySelector('.ql-picker-options');
                if (pickerOptions) {
                    pickerOptions.setAttribute('role', 'listbox');
                    pickerOptions.setAttribute('aria-label', label + ' options');

                    const options = pickerOptions.querySelectorAll('.ql-picker-item');
                    options.forEach(function(option) {
                        option.setAttribute('role', 'option');

                        const dataValue = option.getAttribute('data-value');
                        let optionLabel = '';

                        if (pickerType === 'header') {
                            if (dataValue === null || dataValue === '' || dataValue === 'false') {
                                optionLabel = 'Normal text';
                            } else {
                                optionLabel = 'Heading ' + dataValue;
                            }
                        } else if (pickerType === 'align') {
                            if (dataValue === null || dataValue === '' || dataValue === 'false') {
                                optionLabel = 'Align Left';
                            } else if (dataValue === 'center') {
                                optionLabel = 'Align Center';
                            } else if (dataValue === 'right') {
                                optionLabel = 'Align Right';
                            } else if (dataValue === 'justify') {
                                optionLabel = 'Justify';
                            }
                        } else if (pickerType === 'color' || pickerType === 'background') {
                            if (dataValue) {
                                optionLabel = (pickerType === 'color' ? 'Text color: ' : 'Background color: ') + dataValue;
                            } else {
                                optionLabel = 'Default ' + (pickerType === 'color' ? 'text color' : 'background color');
                            }
                        } else if (pickerType === 'size') {
                            if (dataValue === null || dataValue === '' || dataValue === 'false') {
                                optionLabel = 'Normal size';
                            } else {
                                optionLabel = 'Size ' + dataValue;
                            }
                        } else if (pickerType === 'font') {
                            if (dataValue === null || dataValue === '' || dataValue === 'false') {
                                optionLabel = 'Default font';
                            } else {
                                optionLabel = dataValue + ' font';
                            }
                        } else {
                            optionLabel = dataValue || 'Default';
                        }

                        option.setAttribute('aria-label', optionLabel);
                        option.setAttribute('title', optionLabel);
                    });
                }
            }
        });

        // Update aria-pressed on toggle button click
        toolbar.addEventListener('click', function(e) {
            const button = e.target.closest('button');
            if (button && button.hasAttribute('aria-pressed')) {
                setTimeout(function() {
                    const isActive = button.classList.contains('ql-active');
                    button.setAttribute('aria-pressed', isActive ? 'true' : 'false');
                }, 10);
            }

            // Update aria-expanded for pickers
            const pickerLabel = e.target.closest('.ql-picker-label');
            if (pickerLabel) {
                const picker = pickerLabel.closest('.ql-picker');
                setTimeout(function() {
                    const isExpanded = picker.classList.contains('ql-expanded');
                    pickerLabel.setAttribute('aria-expanded', isExpanded ? 'true' : 'false');
                }, 10);
            }
        });

        // Make the editor content area accessible
        const editor = container.querySelector('.ql-editor');
        if (editor) {
            editor.setAttribute('role', 'textbox');
            editor.setAttribute('aria-multiline', 'true');
            editor.setAttribute('aria-label', 'Rich text editor content');
        }
    };

    /**
     * Get CSRF token from cookies
     */
    Chedito.getCSRFToken = function() {
        const name = 'csrftoken';
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                return decodeURIComponent(cookie.substring(name.length + 1));
            }
        }
        // Try to get from meta tag
        const meta = document.querySelector('meta[name="csrf-token"]');
        if (meta) {
            return meta.getAttribute('content');
        }
        // Try to get from hidden input
        const input = document.querySelector('input[name="csrfmiddlewaretoken"]');
        if (input) {
            return input.value;
        }
        return null;
    };

    /**
     * Upload a file to the server
     */
    Chedito.uploadFile = function(file, uploadUrl, callback) {
        const formData = new FormData();
        formData.append('file', file);

        const xhr = new XMLHttpRequest();
        xhr.open('POST', uploadUrl, true);

        // Add CSRF token
        const csrfToken = Chedito.getCSRFToken();
        if (csrfToken) {
            xhr.setRequestHeader('X-CSRFToken', csrfToken);
        }

        xhr.onload = function() {
            if (xhr.status === 200) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    if (response.success) {
                        callback(null, response.url);
                    } else {
                        callback(response.error || 'Upload failed');
                    }
                } catch (e) {
                    callback('Invalid server response');
                }
            } else {
                try {
                    const response = JSON.parse(xhr.responseText);
                    callback(response.error || 'Upload failed');
                } catch (e) {
                    callback('Upload failed with status ' + xhr.status);
                }
            }
        };

        xhr.onerror = function() {
            callback('Network error during upload');
        };

        xhr.send(formData);
    };

    /**
     * Custom image handler for toolbar button
     */
    Chedito.imageHandler = function(quill, uploadUrl) {
        return function() {
            const input = document.createElement('input');
            input.setAttribute('type', 'file');
            input.setAttribute('accept', 'image/*');
            input.click();

            input.onchange = function() {
                const file = input.files[0];
                if (file) {
                    Chedito.uploadFile(file, uploadUrl, function(error, url) {
                        if (error) {
                            console.error('Image upload failed:', error);
                            alert('Image upload failed: ' + error);
                            return;
                        }
                        const range = quill.getSelection(true);
                        quill.insertEmbed(range.index, 'image', url);
                        quill.setSelection(range.index + 1);
                    });
                }
            };
        };
    };

    /**
     * Custom video handler for toolbar button
     */
    Chedito.videoHandler = function(quill, uploadUrl) {
        return function() {
            const input = document.createElement('input');
            input.setAttribute('type', 'file');
            input.setAttribute('accept', 'video/*');
            input.click();

            input.onchange = function() {
                const file = input.files[0];
                if (file) {
                    Chedito.uploadFile(file, uploadUrl, function(error, url) {
                        if (error) {
                            console.error('Video upload failed:', error);
                            alert('Video upload failed: ' + error);
                            return;
                        }
                        const range = quill.getSelection(true);
                        quill.insertEmbed(range.index, 'video', url);
                        quill.setSelection(range.index + 1);
                    });
                }
            };
        };
    };

    /**
     * Handle drag and drop uploads
     */
    Chedito.setupDragDrop = function(quill, container, imageUrl, videoUrl) {
        container.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.stopPropagation();
            container.classList.add('chedito-dragover');
        });

        container.addEventListener('dragleave', function(e) {
            e.preventDefault();
            e.stopPropagation();
            container.classList.remove('chedito-dragover');
        });

        container.addEventListener('drop', function(e) {
            e.preventDefault();
            e.stopPropagation();
            container.classList.remove('chedito-dragover');

            const files = e.dataTransfer.files;
            for (let file of files) {
                if (file.type.startsWith('image/')) {
                    Chedito.uploadFile(file, imageUrl, function(error, url) {
                        if (error) {
                            console.error('Image upload failed:', error);
                            return;
                        }
                        const range = quill.getSelection(true);
                        quill.insertEmbed(range.index, 'image', url);
                        quill.setSelection(range.index + 1);
                    });
                } else if (file.type.startsWith('video/')) {
                    Chedito.uploadFile(file, videoUrl, function(error, url) {
                        if (error) {
                            console.error('Video upload failed:', error);
                            return;
                        }
                        const range = quill.getSelection(true);
                        quill.insertEmbed(range.index, 'video', url);
                        quill.setSelection(range.index + 1);
                    });
                }
            }
        });
    };

    /**
     * Handle paste uploads
     */
    Chedito.setupPasteUpload = function(quill, imageUrl) {
        quill.root.addEventListener('paste', function(e) {
            const clipboardData = e.clipboardData || window.clipboardData;
            const items = clipboardData.items;

            for (let item of items) {
                if (item.type.indexOf('image') !== -1) {
                    e.preventDefault();
                    const file = item.getAsFile();
                    if (file) {
                        Chedito.uploadFile(file, imageUrl, function(error, url) {
                            if (error) {
                                console.error('Paste upload failed:', error);
                                return;
                            }
                            const range = quill.getSelection(true);
                            quill.insertEmbed(range.index, 'image', url);
                            quill.setSelection(range.index + 1);
                        });
                    }
                    break;
                }
            }
        });
    };

    /**
     * Initialize a Chedito editor
     */
    Chedito.init = function(textareaId, editorId, config, uploadUrls) {
        const textarea = document.getElementById(textareaId);
        const editorContainer = document.getElementById(editorId);

        if (!textarea || !editorContainer) {
            console.error('Chedito: Could not find textarea or editor container');
            return null;
        }

        // Merge configuration
        const finalConfig = Object.assign({}, Chedito.defaults, config || {});

        // Create Quill instance
        const quill = new Quill(editorContainer, finalConfig);

        // Enhance accessibility after Quill creates the toolbar
        const widgetContainer = editorContainer.closest('.chedito-widget-container') || editorContainer.parentElement;
        if (widgetContainer) {
            Chedito.enhanceAccessibility(widgetContainer);
        }

        // Set initial content from textarea
        if (textarea.value) {
            quill.root.innerHTML = textarea.value;
        }

        // Sync content back to textarea on change
        quill.on('text-change', function() {
            const html = quill.root.innerHTML;
            // Convert empty editor to empty string
            if (html === '<p><br></p>' || html === '<p></p>') {
                textarea.value = '';
            } else {
                textarea.value = html;
            }
        });

        // Setup custom handlers if upload URLs provided
        if (uploadUrls) {
            // Custom image handler
            if (uploadUrls.image) {
                const toolbar = quill.getModule('toolbar');
                if (toolbar) {
                    toolbar.addHandler('image', Chedito.imageHandler(quill, uploadUrls.image));
                }
            }

            // Custom video handler
            if (uploadUrls.video) {
                const toolbar = quill.getModule('toolbar');
                if (toolbar) {
                    toolbar.addHandler('video', Chedito.videoHandler(quill, uploadUrls.video));
                }
            }

            // Drag and drop
            Chedito.setupDragDrop(
                quill,
                editorContainer,
                uploadUrls.image || '/chedito/upload/image/',
                uploadUrls.video || '/chedito/upload/video/'
            );

            // Paste upload
            if (uploadUrls.image) {
                Chedito.setupPasteUpload(quill, uploadUrls.image);
            }
        }

        // Store instance
        Chedito.editors[textareaId] = quill;

        // Handle form submission
        const form = textarea.closest('form');
        if (form) {
            form.addEventListener('submit', function() {
                textarea.value = quill.root.innerHTML;
            });
        }

        return quill;
    };

    /**
     * Get an editor instance by textarea ID
     */
    Chedito.getEditor = function(textareaId) {
        return Chedito.editors[textareaId] || null;
    };

    /**
     * Destroy an editor instance
     */
    Chedito.destroy = function(textareaId) {
        const quill = Chedito.editors[textareaId];
        if (quill) {
            // No built-in destroy method in Quill, but we can clean up
            delete Chedito.editors[textareaId];
        }
    };

    /**
     * Auto-initialize all chedito widgets on page load
     */
    Chedito.autoInit = function() {
        const widgets = document.querySelectorAll('[data-chedito-init]');
        widgets.forEach(function(widget) {
            const textareaId = widget.getAttribute('data-textarea-id');
            const editorId = widget.getAttribute('data-editor-id');
            const configStr = widget.getAttribute('data-config');
            const imageUrl = widget.getAttribute('data-upload-image-url');
            const videoUrl = widget.getAttribute('data-upload-video-url');
            const fileUrl = widget.getAttribute('data-upload-file-url');

            let config = {};
            if (configStr) {
                try {
                    config = JSON.parse(configStr);
                } catch (e) {
                    console.error('Chedito: Invalid config JSON');
                }
            }

            const uploadUrls = {
                image: imageUrl,
                video: videoUrl,
                file: fileUrl
            };

            Chedito.init(textareaId, editorId, config, uploadUrls);
        });
    };

    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', Chedito.autoInit);
    } else {
        Chedito.autoInit();
    }

    // Also initialize on Django admin inline add (for dynamic inlines)
    if (typeof django !== 'undefined' && django.jQuery) {
        django.jQuery(document).on('formset:added', function(event, $row, formsetName) {
            setTimeout(Chedito.autoInit, 100);
        });
    }

})();
