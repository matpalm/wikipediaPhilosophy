import java.io.BufferedReader;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.Queue;

public class DistanceToPhilosophy {
  
  private TokenDictionary tokenDictionary = new TokenDictionary();
  
  private final String startNode, edgesFile, redirectFile;
  
  private Map<Integer,List<Integer>> edges = new HashMap<Integer,List<Integer>>();
  
  public static void main(String args[]) throws IOException {
	if (args.length != 3) {
		throw new RuntimeException("DistanceToPhilosophy <startNode> <edgesFile> <redirectFile>");
	}	
    new DistanceToPhilosophy(args).go();
  }
  
  public DistanceToPhilosophy(String[] args) {
    this.startNode = args[0];
    this.edgesFile = args[1];
    this.redirectFile = args[2];
  }
  
  public void go() throws IOException {
    parseInputFile();
    breadthFirstWalk();    
  }

  private void parseInputFile() throws FileNotFoundException, IOException {
    BufferedReader reader = new BufferedReader(new InputStreamReader(System.in));
    String next;    
    int linesProcessed=0;
    
    while((next=reader.readLine())!=null) {
      
      String[] cols = next.split("\t");
      // note: we want the reverse graph
      int toNode = tokenDictionary.tokenForIdx(cols[0]);
      int fromNode = tokenDictionary.tokenForIdx(cols[1]);          
      
      if (edges.containsKey(fromNode)) {
        List<Integer> outboundEdges = edges.get(fromNode);
        if (outboundEdges.contains(toNode)) {
          System.err.println("already and edge from "+fromNode+
              " ("+tokenDictionary.idxToToken.get(fromNode)+") to "+toNode+" ("+tokenDictionary.idxToToken.get(toNode)+")");
        } 
        else {
          outboundEdges.add(toNode);
        }         
      }
      else {        
        List<Integer> newSetOfEdges = new ArrayList<Integer>();
        newSetOfEdges.add(toNode);
        edges.put(fromNode, newSetOfEdges);
      }
      
      if ((++linesProcessed % 1000)==0) {
        System.err.println("slurp input; processed "+linesProcessed);
      }

    }
    
    if (!tokenDictionary.tokenToIdx.containsKey(startNode)) {
      throw new RuntimeException("after parsing stdin never saw starting node ["+startNode+"]");
    }
  }

  private void breadthFirstWalk() {
    Queue<Integer> boundary = new LinkedList<Integer>();
    boundary.add(tokenDictionary.tokenToIdx.get(startNode));
    int distance = 0;    
    while(boundary.size() != 0) {
      Queue<Integer> frontier = new LinkedList<Integer>();
      for(int edge : boundary) {
        System.out.println(tokenDictionary.idxToToken.get(edge) + "\t" + distance);
        if (edges.containsKey(edge)) {
          frontier.addAll(edges.get(edge));
        }
      }
      System.err.println("distance="+distance+" frontier size "+frontier.size());
      distance++;
      boundary = frontier;      
    }
  }
  
}

