/**
 * CREATESONLINE Rich Text Editor
 * Advanced WYSIWYG editor with Wagtail/TinyMCE-level features
 * Pure JavaScript - Zero external dependencies
 *
 * Features:
 * - Text formatting (bold, italic, underline, strikethrough)
 * - Headings (H1-H6)
 * - Text alignment (left, center, right, justify)
 * - Lists (ordered, unordered)
 * - Tables with cell editing
 * - Links with target options
 * - Images (upload, URL, resize, align)
 * - Code blocks with syntax highlighting
 * - Block quotes
 * - Horizontal rules
 * - Text and background colors
 * - Font family and size
 * - Undo/Redo
 * - Find and Replace
 * - Fullscreen mode
 * - HTML source editing
 * - Markdown support
 * - Auto-save
 * - Drag and drop images
 * - Paste from Word/HTML cleanup
 */

(function() {
  'use strict';

  class CreatesonlineRTE {
    constructor(wrapper) {
      this.wrapper = wrapper;
      this.editor = wrapper.querySelector('.rte-editor');
      this.output = wrapper.querySelector('.rte-output');
      this.toolbar = wrapper.querySelector('.rte-toolbar');
      this.targetName = this.editor.dataset.target;

      // Configuration
      this.config = {
        autoSave: this.wrapper.dataset.autosave === 'true',
        autoSaveInterval: parseInt(this.wrapper.dataset.autosaveInterval) || 30000,
        uploadUrl: this.wrapper.dataset.uploadUrl || '/api/uploads',
        maxImageSize: parseInt(this.wrapper.dataset.maxImageSize) || 5 * 1024 * 1024, // 5MB
        allowedImageTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml'],
      };

      // State
      this.history = [];
      this.historyIndex = -1;
      this.isSourceMode = false;
      this.isFullscreen = false;
      this.autoSaveTimer = null;
      this.savedContent = '';

      this.init();
    }

    init() {
      this.setupToolbar();
      this.setupEditor();
      this.setupDragAndDrop();
      this.setupPasteHandler();
      this.setupAutoSave();
      this.saveState();
    }

    setupToolbar() {
      this.toolbar.addEventListener('click', (e) => {
        const btn = e.target.closest('button');
        if (!btn) return;

        e.preventDefault();
        const cmd = btn.dataset.cmd;
        const value = btn.dataset.value;

        // Custom commands
        if (cmd === 'insertTable') {
          this.insertTable();
        } else if (cmd === 'insertImage') {
          this.insertImage();
        } else if (cmd === 'insertImageUrl') {
          this.insertImageUrl();
        } else if (cmd === 'createLink') {
          this.createLink();
        } else if (cmd === 'insertCode') {
          this.insertCodeBlock();
        } else if (cmd === 'foreColor') {
          this.showColorPicker('foreColor');
        } else if (cmd === 'backColor') {
          this.showColorPicker('backColor');
        } else if (cmd === 'fontName') {
          this.showFontPicker();
        } else if (cmd === 'fontSize') {
          this.showFontSizePicker();
        } else if (cmd === 'undo') {
          this.undo();
        } else if (cmd === 'redo') {
          this.redo();
        } else if (cmd === 'findReplace') {
          this.showFindReplace();
        } else if (cmd === 'toggleFullscreen') {
          this.toggleFullscreen();
        } else if (cmd === 'toggleSource') {
          this.toggleSource();
        } else if (cmd === 'insertMarkdown') {
          this.convertMarkdownToHtml();
        } else if (cmd === 'clearFormatting') {
          document.execCommand('removeFormat', false, null);
          this.saveState();
        } else {
          // Standard execCommand
          document.execCommand(cmd, false, value || null);
          this.saveState();
        }

        this.sync();
        this.editor.focus();
      });
    }

    setupEditor() {
      // Sync content on input
      this.editor.addEventListener('input', () => {
        this.sync();
        this.saveState();
      });

      this.editor.addEventListener('blur', () => {
        this.sync();
      });

      // Handle keyboard shortcuts
      this.editor.addEventListener('keydown', (e) => {
        // Ctrl+B - Bold
        if (e.ctrlKey && e.key === 'b') {
          e.preventDefault();
          document.execCommand('bold');
          this.saveState();
        }
        // Ctrl+I - Italic
        else if (e.ctrlKey && e.key === 'i') {
          e.preventDefault();
          document.execCommand('italic');
          this.saveState();
        }
        // Ctrl+U - Underline
        else if (e.ctrlKey && e.key === 'u') {
          e.preventDefault();
          document.execCommand('underline');
          this.saveState();
        }
        // Ctrl+K - Link
        else if (e.ctrlKey && e.key === 'k') {
          e.preventDefault();
          this.createLink();
        }
        // Ctrl+Z - Undo
        else if (e.ctrlKey && e.key === 'z' && !e.shiftKey) {
          e.preventDefault();
          this.undo();
        }
        // Ctrl+Shift+Z or Ctrl+Y - Redo
        else if ((e.ctrlKey && e.shiftKey && e.key === 'z') || (e.ctrlKey && e.key === 'y')) {
          e.preventDefault();
          this.redo();
        }
        // Ctrl+F - Find
        else if (e.ctrlKey && e.key === 'f') {
          e.preventDefault();
          this.showFindReplace();
        }
        // Tab - Insert spaces or list indent
        else if (e.key === 'Tab') {
          e.preventDefault();
          if (e.shiftKey) {
            document.execCommand('outdent');
          } else {
            document.execCommand('indent');
          }
          this.saveState();
        }
      });
    }

    setupDragAndDrop() {
      this.editor.addEventListener('dragover', (e) => {
        e.preventDefault();
        this.editor.classList.add('rte-dragover');
      });

      this.editor.addEventListener('dragleave', () => {
        this.editor.classList.remove('rte-dragover');
      });

      this.editor.addEventListener('drop', (e) => {
        e.preventDefault();
        this.editor.classList.remove('rte-dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
          Array.from(files).forEach(file => {
            if (file.type.startsWith('image/')) {
              this.uploadImage(file);
            }
          });
        }
      });
    }

    setupPasteHandler() {
      this.editor.addEventListener('paste', (e) => {
        // Handle image paste
        const items = e.clipboardData.items;
        for (let item of items) {
          if (item.type.startsWith('image/')) {
            e.preventDefault();
            const file = item.getAsFile();
            this.uploadImage(file);
            return;
          }
        }

        // Clean up HTML paste (from Word, etc.)
        if (e.clipboardData.types.includes('text/html')) {
          e.preventDefault();
          let html = e.clipboardData.getData('text/html');
          html = this.cleanPastedHtml(html);
          document.execCommand('insertHTML', false, html);
          this.saveState();
        }
      });
    }

    cleanPastedHtml(html) {
      // Remove Microsoft Word tags
      html = html.replace(/<\/?o:p>/g, '');
      html = html.replace(/<\/?w:[^>]*>/g, '');
      html = html.replace(/class="Mso[^"]*"/g, '');
      html = html.replace(/style="[^"]*"/g, '');

      // Remove empty spans and divs
      html = html.replace(/<span[^>]*><\/span>/g, '');
      html = html.replace(/<div[^>]*><\/div>/g, '');

      return html;
    }

    setupAutoSave() {
      if (!this.config.autoSave) return;

      this.autoSaveTimer = setInterval(() => {
        const currentContent = this.editor.innerHTML;
        if (currentContent !== this.savedContent) {
          this.savedContent = currentContent;
          this.triggerAutoSave();
        }
      }, this.config.autoSaveInterval);
    }

    triggerAutoSave() {
      // Dispatch custom event for auto-save
      const event = new CustomEvent('rte:autosave', {
        detail: {
          content: this.editor.innerHTML,
          fieldName: this.targetName
        }
      });
      this.wrapper.dispatchEvent(event);

      // Show auto-save indicator
      this.showNotification('Auto-saved', 'success');
    }

    sync() {
      if (this.output) {
        this.output.value = this.editor.innerHTML;
      }
    }

    saveState() {
      const content = this.editor.innerHTML;

      // Remove states after current index
      this.history = this.history.slice(0, this.historyIndex + 1);

      // Add new state
      this.history.push(content);
      this.historyIndex++;

      // Limit history to 50 states
      if (this.history.length > 50) {
        this.history.shift();
        this.historyIndex--;
      }
    }

    undo() {
      if (this.historyIndex > 0) {
        this.historyIndex--;
        this.editor.innerHTML = this.history[this.historyIndex];
        this.sync();
      }
    }

    redo() {
      if (this.historyIndex < this.history.length - 1) {
        this.historyIndex++;
        this.editor.innerHTML = this.history[this.historyIndex];
        this.sync();
      }
    }

    createLink() {
      const selection = window.getSelection();
      const selectedText = selection.toString();

      const modal = this.createModal(`
        <h3>Insert Link</h3>
        <div class="rte-modal-body">
          <label>URL:</label>
          <input type="url" id="link-url" placeholder="https://example.com" value="">
          <label>Text:</label>
          <input type="text" id="link-text" placeholder="Link text" value="${selectedText}">
          <label>
            <input type="checkbox" id="link-target">
            Open in new tab
          </label>
          <div class="rte-modal-actions">
            <button class="rte-btn-primary" id="insert-link">Insert</button>
            <button class="rte-btn-secondary" id="cancel-link">Cancel</button>
          </div>
        </div>
      `);

      modal.querySelector('#insert-link').addEventListener('click', () => {
        const url = modal.querySelector('#link-url').value;
        const text = modal.querySelector('#link-text').value;
        const newTab = modal.querySelector('#link-target').checked;

        if (url) {
          const link = `<a href="${url}"${newTab ? ' target="_blank" rel="noopener noreferrer"' : ''}>${text || url}</a>`;
          document.execCommand('insertHTML', false, link);
          this.saveState();
          this.closeModal(modal);
        }
      });

      modal.querySelector('#cancel-link').addEventListener('click', () => {
        this.closeModal(modal);
      });
    }

    insertTable() {
      const modal = this.createModal(`
        <h3>Insert Table</h3>
        <div class="rte-modal-body">
          <label>Rows:</label>
          <input type="number" id="table-rows" value="3" min="1" max="20">
          <label>Columns:</label>
          <input type="number" id="table-cols" value="3" min="1" max="10">
          <label>
            <input type="checkbox" id="table-header" checked>
            Include header row
          </label>
          <div class="rte-modal-actions">
            <button class="rte-btn-primary" id="insert-table">Insert</button>
            <button class="rte-btn-secondary" id="cancel-table">Cancel</button>
          </div>
        </div>
      `);

      modal.querySelector('#insert-table').addEventListener('click', () => {
        const rows = parseInt(modal.querySelector('#table-rows').value);
        const cols = parseInt(modal.querySelector('#table-cols').value);
        const hasHeader = modal.querySelector('#table-header').checked;

        let html = '<table class="rte-table" border="1" cellpadding="5" cellspacing="0">';

        for (let i = 0; i < rows; i++) {
          html += '<tr>';
          for (let j = 0; j < cols; j++) {
            if (i === 0 && hasHeader) {
              html += '<th contenteditable="true">Header</th>';
            } else {
              html += '<td contenteditable="true">Cell</td>';
            }
          }
          html += '</tr>';
        }

        html += '</table><p><br></p>';

        document.execCommand('insertHTML', false, html);
        this.saveState();
        this.closeModal(modal);
      });

      modal.querySelector('#cancel-table').addEventListener('click', () => {
        this.closeModal(modal);
      });
    }

    insertImage() {
      const input = document.createElement('input');
      input.type = 'file';
      input.accept = this.config.allowedImageTypes.join(',');
      input.multiple = true;

      input.addEventListener('change', () => {
        Array.from(input.files).forEach(file => {
          this.uploadImage(file);
        });
      });

      input.click();
    }

    insertImageUrl() {
      const modal = this.createModal(`
        <h3>Insert Image from URL</h3>
        <div class="rte-modal-body">
          <label>Image URL:</label>
          <input type="url" id="image-url" placeholder="https://example.com/image.jpg">
          <label>Alt text:</label>
          <input type="text" id="image-alt" placeholder="Image description">
          <label>Width (px or %):</label>
          <input type="text" id="image-width" placeholder="auto">
          <div class="rte-modal-actions">
            <button class="rte-btn-primary" id="insert-img">Insert</button>
            <button class="rte-btn-secondary" id="cancel-img">Cancel</button>
          </div>
        </div>
      `);

      modal.querySelector('#insert-img').addEventListener('click', () => {
        const url = modal.querySelector('#image-url').value;
        const alt = modal.querySelector('#image-alt').value;
        const width = modal.querySelector('#image-width').value;

        if (url) {
          let img = `<img src="${url}" alt="${alt}"`;
          if (width) {
            img += ` style="width: ${width}${width.includes('%') ? '' : 'px'}"`;
          }
          img += '>';

          document.execCommand('insertHTML', false, img);
          this.saveState();
          this.closeModal(modal);
        }
      });

      modal.querySelector('#cancel-img').addEventListener('click', () => {
        this.closeModal(modal);
      });
    }

    uploadImage(file) {
      if (!this.config.allowedImageTypes.includes(file.type)) {
        this.showNotification('Invalid file type', 'error');
        return;
      }

      if (file.size > this.config.maxImageSize) {
        this.showNotification('File too large (max 5MB)', 'error');
        return;
      }

      // Show loading indicator
      const loadingId = this.showNotification('Uploading image...', 'info');

      const formData = new FormData();
      formData.append('file', file);

      fetch(this.config.uploadUrl, {
        method: 'POST',
        body: formData
      })
      .then(response => response.json())
      .then(data => {
        this.hideNotification(loadingId);
        if (data.url) {
          const img = `<img src="${data.url}" alt="${file.name}" style="max-width: 100%;">`;
          document.execCommand('insertHTML', false, img);
          this.saveState();
          this.showNotification('Image uploaded', 'success');
        } else {
          throw new Error('No URL in response');
        }
      })
      .catch(error => {
        this.hideNotification(loadingId);
        console.error('Upload error:', error);

        // Fallback: Insert as base64
        const reader = new FileReader();
        reader.onload = (e) => {
          const img = `<img src="${e.target.result}" alt="${file.name}" style="max-width: 100%;">`;
          document.execCommand('insertHTML', false, img);
          this.saveState();
          this.showNotification('Image inserted (local only)', 'warning');
        };
        reader.readAsDataURL(file);
      });
    }

    insertCodeBlock() {
      const selection = window.getSelection();
      const selectedText = selection.toString() || '// Your code here';

      const code = `<pre class="rte-code-block"><code contenteditable="true">${selectedText}</code></pre><p><br></p>`;
      document.execCommand('insertHTML', false, code);
      this.saveState();
    }

    showColorPicker(type) {
      const modal = this.createModal(`
        <h3>Choose Color</h3>
        <div class="rte-modal-body">
          <div class="rte-color-palette">
            ${this.getColorPalette()}
          </div>
          <label>Custom color:</label>
          <input type="color" id="custom-color">
          <div class="rte-modal-actions">
            <button class="rte-btn-primary" id="apply-color">Apply</button>
            <button class="rte-btn-secondary" id="cancel-color">Cancel</button>
          </div>
        </div>
      `);

      const applyColor = (color) => {
        document.execCommand(type, false, color);
        this.saveState();
        this.closeModal(modal);
      };

      modal.querySelectorAll('.rte-color-swatch').forEach(swatch => {
        swatch.addEventListener('click', () => {
          applyColor(swatch.dataset.color);
        });
      });

      modal.querySelector('#apply-color').addEventListener('click', () => {
        const color = modal.querySelector('#custom-color').value;
        applyColor(color);
      });

      modal.querySelector('#cancel-color').addEventListener('click', () => {
        this.closeModal(modal);
      });
    }

    getColorPalette() {
      const colors = [
        '#000000', '#434343', '#666666', '#999999', '#cccccc', '#efefef', '#f3f3f3', '#ffffff',
        '#980000', '#ff0000', '#ff9900', '#ffff00', '#00ff00', '#00ffff', '#4a86e8', '#0000ff',
        '#9900ff', '#ff00ff', '#e91e63', '#9c27b0', '#673ab7', '#3f51b5', '#2196f3', '#03a9f4',
        '#00bcd4', '#009688', '#4caf50', '#8bc34a', '#cddc39', '#ffeb3b', '#ffc107', '#ff9800'
      ];

      return colors.map(color =>
        `<div class="rte-color-swatch" data-color="${color}" style="background: ${color}"></div>`
      ).join('');
    }

    showFontPicker() {
      const fonts = [
        'Arial', 'Arial Black', 'Comic Sans MS', 'Courier New', 'Georgia',
        'Impact', 'Times New Roman', 'Trebuchet MS', 'Verdana', 'Tahoma'
      ];

      const modal = this.createModal(`
        <h3>Choose Font</h3>
        <div class="rte-modal-body">
          <div class="rte-font-list">
            ${fonts.map(font =>
              `<div class="rte-font-item" data-font="${font}" style="font-family: ${font}">${font}</div>`
            ).join('')}
          </div>
        </div>
      `);

      modal.querySelectorAll('.rte-font-item').forEach(item => {
        item.addEventListener('click', () => {
          document.execCommand('fontName', false, item.dataset.font);
          this.saveState();
          this.closeModal(modal);
        });
      });
    }

    showFontSizePicker() {
      const sizes = [1, 2, 3, 4, 5, 6, 7];
      const sizeNames = ['Very Small', 'Small', 'Normal', 'Medium', 'Large', 'Very Large', 'Huge'];

      const modal = this.createModal(`
        <h3>Choose Font Size</h3>
        <div class="rte-modal-body">
          <div class="rte-size-list">
            ${sizes.map((size, i) =>
              `<div class="rte-size-item" data-size="${size}">
                <font size="${size}">${sizeNames[i]}</font>
              </div>`
            ).join('')}
          </div>
        </div>
      `);

      modal.querySelectorAll('.rte-size-item').forEach(item => {
        item.addEventListener('click', () => {
          document.execCommand('fontSize', false, item.dataset.size);
          this.saveState();
          this.closeModal(modal);
        });
      });
    }

    showFindReplace() {
      const modal = this.createModal(`
        <h3>Find and Replace</h3>
        <div class="rte-modal-body">
          <label>Find:</label>
          <input type="text" id="find-text" placeholder="Search...">
          <label>Replace with:</label>
          <input type="text" id="replace-text" placeholder="Replacement...">
          <div class="rte-modal-actions">
            <button class="rte-btn-primary" id="replace-one">Replace</button>
            <button class="rte-btn-primary" id="replace-all">Replace All</button>
            <button class="rte-btn-secondary" id="cancel-find">Cancel</button>
          </div>
        </div>
      `);

      modal.querySelector('#replace-one').addEventListener('click', () => {
        const find = modal.querySelector('#find-text').value;
        const replace = modal.querySelector('#replace-text').value;

        if (find) {
          const content = this.editor.innerHTML;
          this.editor.innerHTML = content.replace(find, replace);
          this.saveState();
          this.sync();
        }
      });

      modal.querySelector('#replace-all').addEventListener('click', () => {
        const find = modal.querySelector('#find-text').value;
        const replace = modal.querySelector('#replace-text').value;

        if (find) {
          const content = this.editor.innerHTML;
          this.editor.innerHTML = content.replaceAll(find, replace);
          this.saveState();
          this.sync();
          this.showNotification('Replaced all occurrences', 'success');
        }
      });

      modal.querySelector('#cancel-find').addEventListener('click', () => {
        this.closeModal(modal);
      });
    }

    toggleFullscreen() {
      this.isFullscreen = !this.isFullscreen;

      if (this.isFullscreen) {
        this.wrapper.classList.add('rte-fullscreen');
        document.body.style.overflow = 'hidden';
      } else {
        this.wrapper.classList.remove('rte-fullscreen');
        document.body.style.overflow = '';
      }
    }

    toggleSource() {
      this.isSourceMode = !this.isSourceMode;

      if (this.isSourceMode) {
        const html = this.editor.innerHTML;
        this.editor.textContent = this.formatHtml(html);
        this.editor.classList.add('rte-source-mode');
      } else {
        const text = this.editor.textContent;
        this.editor.innerHTML = text;
        this.editor.classList.remove('rte-source-mode');
        this.saveState();
      }
    }

    formatHtml(html) {
      // Basic HTML formatting
      return html
        .replace(/></g, '>\n<')
        .replace(/\n\s*\n/g, '\n');
    }

    convertMarkdownToHtml() {
      const modal = this.createModal(`
        <h3>Convert Markdown to HTML</h3>
        <div class="rte-modal-body">
          <label>Paste Markdown:</label>
          <textarea id="markdown-input" rows="10" placeholder="# Heading\n\nParagraph with **bold** and *italic*"></textarea>
          <div class="rte-modal-actions">
            <button class="rte-btn-primary" id="convert-md">Convert</button>
            <button class="rte-btn-secondary" id="cancel-md">Cancel</button>
          </div>
        </div>
      `);

      modal.querySelector('#convert-md').addEventListener('click', () => {
        const markdown = modal.querySelector('#markdown-input').value;
        const html = this.markdownToHtml(markdown);
        document.execCommand('insertHTML', false, html);
        this.saveState();
        this.closeModal(modal);
      });

      modal.querySelector('#cancel-md').addEventListener('click', () => {
        this.closeModal(modal);
      });
    }

    markdownToHtml(markdown) {
      // Simple markdown converter
      let html = markdown;

      // Headers
      html = html.replace(/^###### (.*$)/gim, '<h6>$1</h6>');
      html = html.replace(/^##### (.*$)/gim, '<h5>$1</h5>');
      html = html.replace(/^#### (.*$)/gim, '<h4>$1</h4>');
      html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
      html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
      html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

      // Bold
      html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      html = html.replace(/__(.*?)__/g, '<strong>$1</strong>');

      // Italic
      html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
      html = html.replace(/_(.*?)_/g, '<em>$1</em>');

      // Links
      html = html.replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2">$1</a>');

      // Images
      html = html.replace(/!\[(.*?)\]\((.*?)\)/g, '<img src="$2" alt="$1">');

      // Code
      html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

      // Lists
      html = html.replace(/^\* (.*$)/gim, '<li>$1</li>');
      html = html.replace(/^\d+\. (.*$)/gim, '<li>$1</li>');

      // Paragraphs
      html = html.replace(/\n\n/g, '</p><p>');
      html = '<p>' + html + '</p>';

      return html;
    }

    createModal(content) {
      const overlay = document.createElement('div');
      overlay.className = 'rte-modal-overlay';

      const modal = document.createElement('div');
      modal.className = 'rte-modal';
      modal.innerHTML = content;

      overlay.appendChild(modal);
      document.body.appendChild(overlay);

      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
          this.closeModal(overlay);
        }
      });

      return overlay;
    }

    closeModal(modal) {
      modal.remove();
    }

    showNotification(message, type = 'info') {
      const id = 'notification-' + Date.now();
      const notification = document.createElement('div');
      notification.id = id;
      notification.className = `rte-notification rte-notification-${type}`;
      notification.textContent = message;

      document.body.appendChild(notification);

      setTimeout(() => {
        notification.classList.add('rte-notification-show');
      }, 10);

      setTimeout(() => {
        this.hideNotification(id);
      }, 3000);

      return id;
    }

    hideNotification(id) {
      const notification = document.getElementById(id);
      if (notification) {
        notification.classList.remove('rte-notification-show');
        setTimeout(() => notification.remove(), 300);
      }
    }

    destroy() {
      if (this.autoSaveTimer) {
        clearInterval(this.autoSaveTimer);
      }
    }
  }

  // Initialize all editors on page load
  document.addEventListener('DOMContentLoaded', () => {
    const editors = document.querySelectorAll('.rte');
    editors.forEach(wrapper => {
      new CreatesonlineRTE(wrapper);
    });
  });

  // Export for manual initialization
  window.CreatesonlineRTE = CreatesonlineRTE;
})();