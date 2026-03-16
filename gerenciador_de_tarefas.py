import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from datetime import datetime

class GerenciadorTarefas:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Tarefas")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        
        # arquivo para salvar as tarefas
        self.arquivo_tarefas = "tarefas.json"
        
        # lista de tarefas
        self.tarefas = []
        
        # Carregar tarefas salvas
        self.carregar_tarefas()
        
        # Configurar interface
        self.setup_interface()
        
    def setup_interface(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        titulo = ttk.Label(main_frame, text="📋 GERENCIADOR DE TAREFAS", 
                          font=('Arial', 16, 'bold'))
        titulo.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Frame para entrada de nova tarefa
        frame_entrada = ttk.Frame(main_frame)
        frame_entrada.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(frame_entrada, text="Nova Tarefa:").grid(row=0, column=0, padx=(0, 5))
        
        self.entry_tarefa = ttk.Entry(frame_entrada, width=40)
        self.entry_tarefa.grid(row=0, column=1, padx=(0, 5))
        self.entry_tarefa.bind('<Return>', lambda e: self.adicionar_tarefa())
        
        ttk.Button(frame_entrada, text="Adicionar", 
                  command=self.adicionar_tarefa).grid(row=0, column=2)
        
        # Frame para filtros
        frame_filtros = ttk.Frame(main_frame)
        frame_filtros.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(frame_filtros, text="Filtrar:").grid(row=0, column=0, padx=(0, 5))
        
        self.filtro_var = tk.StringVar(value="Todas")
        filtros = ttk.Combobox(frame_filtros, textvariable=self.filtro_var, 
                              values=["Todas", "Pendentes", "Concluídas"], 
                              state="readonly", width=15)
        filtros.grid(row=0, column=1, padx=(0, 5))
        filtros.bind('<<ComboboxSelected>>', lambda e: self.atualizar_lista())
        
        # Frame para a lista de tarefas
        frame_lista = ttk.Frame(main_frame)
        frame_lista.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_lista)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox com cores personalizadas
        self.lista_tarefas = tk.Listbox(frame_lista, width=60, height=15, 
                                        yscrollcommand=scrollbar.set,
                                        selectmode=tk.SINGLE,
                                        font=('Arial', 10))
        self.lista_tarefas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.lista_tarefas.yview)
        
        # frame para botões de ação
        frame_botoes = ttk.Frame(main_frame)
        frame_botoes.grid(row=4, column=0, columnspan=3, pady=(0, 10))
        
        ttk.Button(frame_botoes, text="✅ Marcar como Concluída", 
                  command=self.marcar_concluida).grid(row=0, column=0, padx=5)
        
        ttk.Button(frame_botoes, text="❌ Remover Selecionada", 
                  command=self.remover_tarefa).grid(row=0, column=1, padx=5)
        
        ttk.Button(frame_botoes, text="📊 Estatísticas", 
                  command=self.mostrar_estatisticas).grid(row=0, column=2, padx=5)
        
        # Frame para estatísticas rápidas
        self.frame_stats = ttk.LabelFrame(main_frame, text="Resumo", padding="5")
        self.frame_stats.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.label_stats = ttk.Label(self.frame_stats, text="", font=('Arial', 9))
        self.label_stats.pack()
        
        # Atualizar lista
        self.atualizar_lista()
        
    def adicionar_tarefa(self):
        """Adiciona uma nova tarefa"""
        tarefa_texto = self.entry_tarefa.get().strip()
        
        if tarefa_texto:
            # Criar dicionário para a tarefa
            tarefa = {
                'id': len(self.tarefas) + 1,
                'texto': tarefa_texto,
                'concluida': False,
                'data_criacao': datetime.now().strftime("%d/%m/%Y %H:%M"),
                'data_conclusao': None
            }
            
            self.tarefas.append(tarefa)
            self.entry_tarefa.delete(0, tk.END)
            self.salvar_tarefas()
            self.atualizar_lista()
            messagebox.showinfo("Sucesso", "Tarefa adicionada com sucesso!")
        else:
            messagebox.showwarning("Aviso", "Digite uma tarefa!")
    
    def marcar_concluida(self):
        """Marca a tarefa selecionada como concluída"""
        selecao = self.lista_tarefas.curselection()
        
        if selecao:
            # Obter índice real baseado no filtro atual
            indices_reais = self.obter_indices_filtrados()
            indice_real = indices_reais[selecao[0]]
            
            if not self.tarefas[indice_real]['concluida']:
                self.tarefas[indice_real]['concluida'] = True
                self.tarefas[indice_real]['data_conclusao'] = datetime.now().strftime("%d/%m/%Y %H:%M")
                self.salvar_tarefas()
                self.atualizar_lista()
                messagebox.showinfo("Sucesso", "Tarefa marcada como concluída!")
            else:
                messagebox.showinfo("Info", "Esta tarefa já está concluída!")
        else:
            messagebox.showwarning("Aviso", "Selecione uma tarefa!")
    
    def remover_tarefa(self):
        """Remove a tarefa selecionada"""
        selecao = self.lista_tarefas.curselection()
        
        if selecao:
            # Confirmar remoção
            if messagebox.askyesno("Confirmar", "Deseja realmente remover esta tarefa?"):
                # Obter índice real baseado no filtro atual
                indices_reais = self.obter_indices_filtrados()
                indice_real = indices_reais[selecao[0]]
                
                tarefa_removida = self.tarefas.pop(indice_real)
                
                # Reordenar IDs
                for i, tarefa in enumerate(self.tarefas):
                    tarefa['id'] = i + 1
                
                self.salvar_tarefas()
                self.atualizar_lista()
                messagebox.showinfo("Sucesso", "Tarefa removida!")
        else:
            messagebox.showwarning("Aviso", "Selecione uma tarefa!")
    
    def obter_indices_filtrados(self):
        """Retorna os índices reais das tarefas baseado no filtro atual"""
        filtro = self.filtro_var.get()
        indices_reais = []
        
        for i, tarefa in enumerate(self.tarefas):
            if filtro == "Todas":
                indices_reais.append(i)
            elif filtro == "Pendentes" and not tarefa['concluida']:
                indices_reais.append(i)
            elif filtro == "Concluídas" and tarefa['concluida']:
                indices_reais.append(i)
        
        return indices_reais
    
    def atualizar_lista(self):
        """Atualiza a lista de tarefas na interface"""
        self.lista_tarefas.delete(0, tk.END)
        
        filtro = self.filtro_var.get()
        
        for tarefa in self.tarefas:
            # Aplicar filtro
            if filtro == "Pendentes" and tarefa['concluida']:
                continue
            elif filtro == "Concluídas" and not tarefa['concluida']:
                continue
            
            # Formatar texto da tarefa
            if tarefa['concluida']:
                texto = f"✅ [{tarefa['id']}] {tarefa['texto']} (Concluída em: {tarefa['data_conclusao']})"
                self.lista_tarefas.insert(tk.END, texto)
                # Aplicar cor verde para tarefas concluídas
                self.lista_tarefas.itemconfig(tk.END, fg='green')
            else:
                texto = f"⭕ [{tarefa['id']}] {tarefa['texto']} (Criada em: {tarefa['data_criacao']})"
                self.lista_tarefas.insert(tk.END, texto)
                # Aplicar cor azul para tarefas pendentes
                self.lista_tarefas.itemconfig(tk.END, fg='blue')
        
        # Atualizar estatísticas
        self.atualizar_estatisticas()
    
    def atualizar_estatisticas(self):
        """Atualiza as estatísticas rápidas"""
        total = len(self.tarefas)
        concluidas = sum(1 for t in self.tarefas if t['concluida'])
        pendentes = total - concluidas
        
        if total > 0:
            percentual = (concluidas / total) * 100
            stats_text = f"Total: {total} | Pendentes: {pendentes} | Concluídas: {concluidas} ({percentual:.1f}%)"
        else:
            stats_text = "Nenhuma tarefa cadastrada"
        
        self.label_stats.config(text=stats_text)
    
    def mostrar_estatisticas(self):
        """Mostra estatísticas detalhadas"""
        total = len(self.tarefas)
        concluidas = sum(1 for t in self.tarefas if t['concluida'])
        pendentes = total - concluidas
        
        if total > 0:
            percentual = (concluidas / total) * 100
            mensagem = f"📊 ESTATÍSTICAS 📊\n\n"
            mensagem += f"Total de tarefas: {total}\n"
            mensagem += f"Tarefas pendentes: {pendentes}\n"
            mensagem += f"Tarefas concluídas: {concluidas}\n"
            mensagem += f"Progresso: {percentual:.1f}% concluído"
        else:
            mensagem = "Nenhuma tarefa cadastrada ainda!"
        
        messagebox.showinfo("Estatísticas", mensagem)
    
    def salvar_tarefas(self):
        """Salva as tarefas em arquivo JSON"""
        try:
            with open(self.arquivo_tarefas, 'w', encoding='utf-8') as f:
                json.dump(self.tarefas, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar tarefas: {e}")
    
    def carregar_tarefas(self):
        """Carrega as tarefas do arquivo JSON"""
        try:
            if os.path.exists(self.arquivo_tarefas):
                with open(self.arquivo_tarefas, 'r', encoding='utf-8') as f:
                    self.tarefas = json.load(f)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar tarefas: {e}")
            self.tarefas = []

def main():
    root = tk.Tk()
    app = GerenciadorTarefas(root)
    root.mainloop()

if __name__ == "__main__":
    main()